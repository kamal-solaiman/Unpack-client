#include "history.hpp"
#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#endif
using namespace history;
struct Config {
    std::vector<fs::path> archives, extras;   // archives: files or directories; extras: name dictionaries
    fs::path exe, out="History-output";
    bool unresolved=false;
};
struct NameSources {
    fs::path bundled, exe;
    std::vector<fs::path> extras;
};
static std::string quote(const std::string& s) {
    std::string r="\""; for(char c:s) { if(c=='"') r+='"'; r+=c; } return r+'"';
}
static Bytes bytes(const std::string& s) { return Bytes(s.begin(),s.end()); }
// Semicolon-separated path lists keep multi-value options usable from one menu prompt.
static std::vector<fs::path> splitPaths(const std::string& text) {
    std::vector<fs::path> out; std::istringstream in(text); std::string item;
    while(std::getline(in,item,';')) {
        size_t b=item.find_first_not_of(" \t\r\n"),e=item.find_last_not_of(" \t\r\n");
        if(b==std::string::npos) continue;
        item=item.substr(b,e-b+1);
        if(item.size()>=2 && item.front()=='"' && item.back()=='"') item=item.substr(1,item.size()-2);
        out.push_back(fs::u8path(item));
    }
    return out;
}
static uint64_t fileSize(const fs::path& p) {
    std::error_code ec; auto n=fs::file_size(p,ec); return ec ? 0u : static_cast<uint64_t>(n);
}
// Output folder name for one archive inside a batch run.
static std::string folderName(const fs::path& archive) {
    std::string base;
    for(unsigned char c:archive.filename().u8string())
        base+=(std::isalnum(c) || c=='.' || c=='-' || c=='_') ? char(c) : '_';
    auto dot=base.rfind('.');
    if(dot!=std::string::npos && dot>0) base=base.substr(0,dot);
    if(base.empty() || base=="." || base=="..") base="archive";
    if(base.size()>64) base=base.substr(0,64);
    return base;
}
static void usage() {
    std::cout<<R"(History Unpacker - History D2 archives
Usage: HistoryUnpacker [options] [command] [argument]
Commands:
  menu                 Interactive English menu (default)
  scan                 Find and validate every History D2 archive in scope
  info                 Inspect archive format and entry sizes
  keys                 Extract header key/IV and validate against a payload
  list                 Recover and list names; unresolved names remain explicit
  verify               Decrypt, decompress and verify every entry (no output files)
  extract NAME         Extract one entry by original virtual filename
  all                  Extract all resolved files; skip unresolved by default
  manifest FILE.csv    Export entry metadata and recovered-name mapping
Options:
  --archive PATH       History archive file or a directory to scan; repeatable.
                       A directory is searched recursively (pack\ first).
                       Extension does not matter; the D2 magic decides.
  --exe FILE           Read executable references for name recovery; never execute it
  --names FILE         Additional names, one original virtual path per line; repeatable
  --out DIRECTORY      Extraction destination (default: History-output)
  --include-unresolved Export unknown names as _unresolved/HASH.unresolved
  --help               Show this help
Every command runs over all selected archives. Files are written to
--out\<archive folder>\ and a combined CSV to --out\history-manifest-all.csv.
Existing files are never overwritten. No type/extension whitelist is applied.
A CRC32 filename hash is not reversible; names are recovered from candidates.
)";
}
// Expands every configured file/directory argument into a concrete archive list.
static std::vector<fs::path> prepare(const Config& c) {
    std::vector<fs::path> out; std::set<fs::path> seen;
    for(const auto& path:c.archives)
        for(auto& found:resolveArchiveArgument(path))
            if(seen.insert(fs::absolute(found).lexically_normal()).second) out.push_back(found);
    if(out.empty()) throw std::runtime_error(
        "No History D2 archive found. Pass --archive FILE, or --archive DIRECTORY to scan "
        "a folder (for example the client pack directory).");
    return out;
}
static NameSources sources(const Config& c, const fs::path& bundled) { return {bundled,c.exe,c.extras}; }
static void recover(Names& names,const Archive& archive,const NameSources& s) {
    std::error_code ec;
    if(!s.bundled.empty()) names.load(s.bundled);
    for(const auto& extra:s.extras) names.load(extra);
    if(!s.exe.empty()) {
        if(!fs::is_regular_file(s.exe,ec)) std::cerr<<"Warning: executable not readable: "<<s.exe.string()<<'\n';
        else {
            try {
                auto b=readFile(s.exe,MaxFile);
                if(b.size()<64 || b[0]!='M' || b[1]!='Z') throw std::runtime_error("Executable is not a PE/MZ file");
                names.scan(b);
            } catch(const std::exception& ex) { std::cerr<<"Warning: executable scan skipped: "<<ex.what()<<'\n'; }
        }
    }
    size_t failed=0;
    for(const auto& e:archive.entries) {
        try { names.scan(archive.decode(e)); }
        catch(const std::exception&) { ++failed; }
    }
    std::cout<<"Recovered "<<names.resolved()<<" / "<<archive.entries.size()<<" names from CRC-matched references.\n";
    if(failed) std::cout<<"Warning: "<<failed<<" payloads could not be scanned. Run verify for details.\n";
}
static void printHex(const Bytes& data) {
    const char* h="0123456789abcdef";
    for(uint8_t b:data) std::cout<<h[b>>4]<<h[b&15];
    std::cout<<'\n';
}
static int cmdScan(const std::vector<fs::path>& archives) {
    std::cout<<"History D2 archives in scope: "<<archives.size()<<'\n';
    size_t good=0;
    for(const auto& path:archives) {
        std::cout<<"\n--- "<<path.string()<<" ("<<fileSize(path)<<" bytes) ---\n";
        try {
            Archive a(path);
            if(a.entries.empty()) { std::cout<<"Entries: 0 (valid header, empty archive)\n"; ++good; continue; }
            try { a.decode(a.entries.front()); ++good; }
            catch(const std::exception& ex) { std::cerr<<"Key/IV validation failed: "<<ex.what()<<'\n'; }
            std::cout<<"Entries: "<<a.entries.size()<<'\n';
        } catch(const std::exception& ex) { std::cerr<<"Rejected: "<<ex.what()<<'\n'; }
    }
    std::cout<<"\nUsable archives: "<<good<<" / "<<archives.size()<<'\n';
    std::cout<<"Run a command without --archive to process all of them at once.\n";
    return good==archives.size() ? 0 : 1;
}
static int cmdInfo(const std::vector<fs::path>& archives) {
    size_t bad=0,totalEntries=0; uint64_t totalStored=0,totalRaw=0;
    for(size_t i=0;i<archives.size();++i) {
        const bool many=archives.size()>1;
        if(many) std::cout<<(i?"\n":"")<<"=== Archive "<<(i+1)<<" / "<<archives.size()<<": "<<archives[i].string()<<" ===\n";
        try {
            Archive a(archives[i]);
            uint64_t raw=0,stored=0; for(const auto& e:a.entries) { raw+=e.size; stored+=e.stored; }
            if(!many) std::cout<<"Archive: "<<archives[i].string()<<'\n';
            std::cout<<"Format: History D2 / F00FED5C\nCipher: AES-256-CFB128 (reset IV per entry)\n"
                     <<"Compression: raw LZ4\nIntegrity: XXH32, seed F00FED5C\n"
                     <<"Names: CRC32, lowercase / separators\n"
                     <<"Entries: "<<a.entries.size()<<"\nStored bytes: "<<stored<<"\nDecoded bytes: "<<raw<<'\n';
            totalEntries+=a.entries.size(); totalStored+=stored; totalRaw+=raw;
        } catch(const std::exception& ex) { ++bad; std::cerr<<"Error: "<<ex.what()<<'\n'; }
    }
    if(archives.size()>1)
        std::cout<<"\nArchives: "<<archives.size()<<"; entries: "<<totalEntries<<"; stored bytes: "
                 <<totalStored<<"; decoded bytes: "<<totalRaw<<'\n';
    return bad?1:0;
}
static int cmdKeys(const std::vector<fs::path>& archives) {
    size_t bad=0;
    for(const auto& path:archives) {
        if(archives.size()>1) std::cout<<"\n=== "<<path.string()<<" ===\n";
        try {
            Archive a(path);
            if(a.entries.empty()) throw std::runtime_error("Empty archive: key cannot be validated");
            a.decode(a.entries.front());
            std::cout<<"Key source: archive header, not a guessed EXE byte sequence.\n"
                     <<"Validated with first entry's decompression and XXH32 checksum.\nAES-256 key: ";
            printHex(Bytes(a.key.begin(),a.key.end()));
            std::cout<<"CFB128 IV: "; printHex(Bytes(a.iv.begin(),a.iv.end()));
            std::cout<<"This History profile needs no executable XOR mask. Other variants may differ.\n";
        } catch(const std::exception& ex) { ++bad; std::cerr<<"Error: "<<ex.what()<<'\n'; }
    }
    return bad?1:0;
}
static int cmdVerify(const std::vector<fs::path>& archives) {
    size_t good=0,failed=0,bad=0,total=0;
    for(size_t i=0;i<archives.size();++i) {
        if(archives.size()>1) std::cout<<(i?"\n":"")<<"=== "<<archives[i].string()<<" ===\n";
        try {
            Archive a(archives[i]);
            for(const auto& e:a.entries) {
                try { a.decode(e); ++good; }
                catch(const std::exception& ex) { ++failed; std::cerr<<hex32(e.hash)<<": "<<ex.what()<<'\n'; }
            }
            total+=a.entries.size();
        } catch(const std::exception& ex) { ++bad; std::cerr<<"Error: "<<ex.what()<<'\n'; }
    }
    if(archives.size()>1) std::cout<<(total?"\n":"")<<"All archives - ";
    std::cout<<"Verified: "<<good<<"; failed: "<<failed<<"; total: "<<total<<'\n';
    if(archives.size()>1) std::cout<<"Archives: "<<archives.size()<<"; unreadable: "<<bad<<'\n';
    return (failed||bad)?1:0;
}
static int cmdExtract(const std::vector<fs::path>& archives,const std::string& arg,const Config& c) {
    if(arg.empty()) throw std::runtime_error("An original filename is required");
    auto h=nameHash(arg);
    for(const auto& path:archives) {
        try {
            Archive a(path);
            auto it=std::find_if(a.entries.begin(),a.entries.end(),[&](const Entry& e){return e.hash==h;});
            if(it==a.entries.end()) continue;
            auto rel=safeRelative(arg); writeExclusive(c.out,rel,a.decode(*it));
            std::cout<<"Extracted: "<<(c.out/rel).string()<<" (content checksum verified)\n";
            if(archives.size()>1) std::cout<<"Source archive: "<<path.string()<<'\n';
            return 0;
        } catch(const std::exception& ex) { std::cerr<<"Error: "<<path.string()<<": "<<ex.what()<<'\n'; }
    }
    throw std::runtime_error("Filename not found in any selected archive (CRC32 "+hex32(h)+")");
}
// One selected archive plus its output folder inside a batch run.
struct Unit {
    fs::path path, folder;
    Archive archive;
    explicit Unit(const fs::path& p,const fs::path& f):path(p),folder(f),archive(p) {}
};
static std::vector<Unit> openBatch(const std::vector<fs::path>& archives,std::vector<std::string>& errors) {
    std::vector<Unit> units; std::set<std::string> used;
    for(const auto& path:archives) {
        std::string base=folderName(path),name=base;
        for(size_t n=2;!used.insert(name).second;++n) name=base+"-"+std::to_string(n);
        try { units.emplace_back(path,fs::u8path(name)); }
        catch(const std::exception& ex) { errors.push_back(path.string()+": "+ex.what()); }
    }
    if(units.empty()) throw std::runtime_error("No archive could be opened: "+errors.front());
    return units;
}
static int cmdList(std::vector<Unit>& units,const NameSources& s) {
    for(const auto& unit:units) {
        if(units.size()>1) std::cout<<"\n=== "<<unit.path.string()<<" ("<<unit.archive.entries.size()<<" entries) ===\n";
        Names names(unit.archive); recover(names,unit.archive,s);
        for(const auto& e:unit.archive.entries) {
            auto n=names.get(e.hash);
            std::cout<<hex32(e.hash)<<'\t'<<e.size<<'\t'<<(n.empty()?"[unresolved or ambiguous]":n)<<'\n';
        }
    }
    return 0;
}
static int cmdBatch(const std::string& command,const std::string& arg,std::vector<Unit>& units,
                    const Config& c,const NameSources& s) {
    if(command=="manifest" && arg.empty()) throw std::runtime_error("Manifest path is required");
    // Each archive gets its own output folder so files with equal names never collide.
    std::set<std::string> used;
    for(auto& unit:units) {
        std::string base=folderName(unit.path),name=base;
        for(size_t n=2;!used.insert(name).second;++n) name=base+"-"+std::to_string(n);
        unit.folder=fs::u8path(name);
    }
    // "manifest" writes exactly one CSV at the requested path and no payload.
    // "all" writes one CSV per archive plus a combined CSV for the whole selection.
    const bool combinedOnly=command=="manifest";
    const fs::path combinedPath=combinedOnly ? fs::u8path(arg) : c.out/"history-manifest-all.csv";
    auto requireFree=[&](const fs::path& p) {
        if(fs::exists(fs::symlink_status(p)))
            throw std::runtime_error("Manifest already exists; choose a fresh output directory/path: "+p.string());
    };
    requireFree(combinedPath);
    if(!combinedOnly) for(const auto& unit:units) requireFree(c.out/unit.folder/"history-manifest.csv");
    std::ostringstream combined;
    combined<<"archive,output_folder,name_crc32,original_candidate,output_path,decoded_size,stored_size,xxh32,status,detail\n";
    size_t done=0,skipped=0,failed=0;
    for(size_t i=0;i<units.size();++i) {
        auto& unit=units[i];
        if(units.size()>1) std::cout<<(i?"\n":"")<<"=== "<<unit.path.string()<<" ===\n";
        std::ostringstream report;
        report<<"name_crc32,original_candidate,output_path,decoded_size,stored_size,xxh32,status,detail\n";
        Names names(unit.archive); recover(names,unit.archive,s);
        size_t unitDone=0,unitSkipped=0,unitFailed=0;
        for(const auto& e:unit.archive.entries) {
            std::string name=names.get(e.hash),destination,status,detail;
            if(command=="manifest") status=name.empty()?"unresolved_or_ambiguous":"crc_matched_candidate";
            else if(name.empty() && !c.unresolved) { status="skipped_unresolved"; ++unitSkipped; }
            else {
                try {
                    auto rel=name.empty()? fs::path("_unresolved")/(hex32(e.hash)+".unresolved") : safeRelative(name);
                    destination=(unit.folder/rel).generic_u8string();
                    writeExclusive(c.out/unit.folder,rel,unit.archive.decode(e));
                    status=name.empty()?"verified_unresolved":"verified_extracted"; ++unitDone;
                } catch(const std::exception& ex) {
                    status="failed"; detail=ex.what(); ++unitFailed;
                    std::cerr<<hex32(e.hash)<<": "<<detail<<'\n';
                }
            }
            std::string line=hex32(e.hash)+','+quote(name)+','+quote(destination)+','+std::to_string(e.size)+','
                            +std::to_string(e.stored)+','+hex32(e.checksum)+','+status+','+quote(detail);
            report<<line<<'\n';
            combined<<quote(unit.path.generic_u8string())<<','<<quote(unit.folder.generic_u8string())<<','<<line<<'\n';
        }
        done+=unitDone; skipped+=unitSkipped; failed+=unitFailed;
        if(!combinedOnly) {
            fs::path reportPath=c.out/unit.folder/"history-manifest.csv";
            writeExclusive(reportPath.parent_path(),reportPath.filename(),bytes(report.str()));
            std::cout<<"Manifest: "<<reportPath.string()<<'\n';
            std::cout<<"Extracted: "<<unitDone<<"; unresolved skipped: "<<unitSkipped<<"; failed: "<<unitFailed<<'\n';
        }
    }
    writeExclusive(combinedPath.has_parent_path()?combinedPath.parent_path():fs::path("."),
                   combinedPath.filename(),bytes(combined.str()));
    std::cout<<"Manifest: "<<combinedPath.string()<<'\n';
    // One archive already printed its own totals; only a batch needs the summary line.
    if(command=="all" && units.size()>1)
        std::cout<<"\nArchives: "<<units.size()<<"; Extracted: "<<done<<"; unresolved skipped: "<<skipped
                 <<"; failed: "<<failed<<'\n';
    return failed?1:(skipped?2:0);
}
static int run(const std::string& command,const std::string& arg,const Config& c,const fs::path& bundled) {
    if(command=="scan") return cmdScan(prepare(c));
    auto archives=prepare(c);
    if(command=="info") return cmdInfo(archives);
    if(command=="keys") return cmdKeys(archives);
    if(command=="verify") return cmdVerify(archives);
    if(command=="extract") return cmdExtract(archives,arg,c);
    if(command!="list" && command!="manifest" && command!="all") throw std::runtime_error("Unknown command: "+command);
    std::vector<std::string> errors;
    auto units=openBatch(archives,errors);
    for(const auto& e:errors) std::cerr<<"Error: "<<e<<'\n';
    auto s=sources(c,bundled);
    return command=="list" ? cmdList(units,s) : cmdBatch(command,arg,units,c,s);
}
static std::string prompt(const std::string& text) {
    std::cout<<text; std::string line;
    if(!std::getline(std::cin,line)) throw std::runtime_error("Input closed");
    if(line.size()>=2 && line.front()=='"' && line.back()=='"') line=line.substr(1,line.size()-2);
    return line;
}
static int menu(Config c,const fs::path& bundled) {
    bool firstPrompt=true;
    while(true) {
        // A missing archive must not close the menu: option 9 sets a new path.
        std::vector<fs::path> archives; std::string problem;
        try { archives=prepare(c); }
        catch(const std::exception& ex) { problem=ex.what(); }
        std::cout<<"\n=== History Unpacker ===\n";
        if(problem.empty()) {
            std::cout<<"Archives ("<<archives.size()<<"):\n";
            size_t shown=std::min<size_t>(archives.size(),8);
            for(size_t i=0;i<shown;++i) std::cout<<"  - "<<archives[i].string()<<'\n';
            if(archives.size()>shown) std::cout<<"  ... "<<(archives.size()-shown)<<" more (option 3 lists all)\n";
        } else {
            std::cout<<"Archives: none\n"<<problem<<'\n';
        }
        std::cout<<"Output: "<<c.out.string()
                 <<"\n1. Inspect archives\n2. Extract and validate key / IV\n3. Scan directory for archives\n"
                 <<"4. Recover and list filenames\n5. Decrypt one file by name\n6. Decrypt all files (every archive)\n"
                 <<"7. Verify all payloads\n8. Export filename manifest\n"
                 <<"9. Change archive / output paths\n10. Set executable / additional name lists\n"
                 <<"11. Toggle unresolved export (currently "<<(c.unresolved?"ON":"OFF")<<")\n0. Exit\n";
        std::string choice; std::cout<<"> ";
        if(!std::getline(std::cin,choice)) {
            // Explain instead of closing silently when the window cannot receive input.
            if(firstPrompt) std::cout<<"\nConsole input closed before any selection was made.\n"
                "If you started this program by double-clicking and it closed immediately,\n"
                "open a command prompt in this folder and run the EXE from there.\n";
            return 0;
        }
        firstPrompt=false;
        if(choice=="0") return 0;
        try {
            if(choice=="1") run("info","",c,bundled);
            else if(choice=="2") run("keys","",c,bundled);
            else if(choice=="3") run("scan","",c,bundled);
            else if(choice=="4") run("list","",c,bundled);
            else if(choice=="5") run("extract",prompt("Original virtual filename: "),c,bundled);
            else if(choice=="6") run("all","",c,bundled);
            else if(choice=="7") run("verify","",c,bundled);
            else if(choice=="8") run("manifest",prompt("New manifest CSV path: "),c,bundled);
            else if(choice=="9") {
                auto paths=splitPaths(prompt("Archive file(s) or directory (blank = auto-discover): "));
                if(!paths.empty()) c.archives=paths;
                c.out=fs::u8path(prompt("Output directory: "));
            }
            else if(choice=="10") {
                c.exe=fs::u8path(prompt("History executable (blank = none): "));
                c.extras=splitPaths(prompt("Extra name lists, ';' separated (blank = none): "));
            }
            else if(choice=="11") c.unresolved=!c.unresolved;
            else std::cout<<"Unknown selection.\n";
        } catch(const std::exception& ex) { std::cerr<<"Error: "<<ex.what()<<'\n'; }
    }
}
static int appMain(int argc,char** argv) {
    try {
        Config c; fs::path bundled;
        std::string command="menu",arg; bool haveCommand=false;
        for(int i=1;i<argc;++i) {
            std::string v=argv[i];
            if(v=="--help") { usage(); return 0; }
            if(v=="--include-unresolved") { c.unresolved=true; continue; }
            if(v=="--archive" || v=="--exe" || v=="--names" || v=="--out") {
                if(++i>=argc) throw std::runtime_error("Missing option value: "+v);
                auto path=fs::u8path(argv[i]);
                if(v=="--archive") c.archives.push_back(path);
                else if(v=="--exe") c.exe=path;
                else if(v=="--names") c.extras.push_back(path);
                else c.out=path;
            } else if(v.rfind("--",0)==0) throw std::runtime_error("Unknown option: "+v);
            else if(!haveCommand) { command=v; haveCommand=true; }
            else if(arg.empty()) arg=v;
            else throw std::runtime_error("Too many arguments; quote paths containing spaces");
        }
        if(c.archives.empty()) {
            // Locate assets from the working directory or next to the built executable.
            // Every History D2 archive found this way is processed, not just workplace.d2.
            std::vector<fs::path> found;
            for(const auto& start:{fs::current_path(),fs::absolute(fs::u8path(argv[0])).parent_path()}) {
                discoverAssets(start,found,c.exe,bundled);
                if(!found.empty()) break;
            }
            c.archives=found;
        }
        if(command=="menu") return menu(c,bundled);
        return run(command,arg,c,bundled);
    } catch(const std::exception& ex) { std::cerr<<"Error: "<<ex.what()<<'\n'; return 1; }
      catch(...) { std::cerr<<"Error: unknown failure\n"; return 1; }
}

#ifdef _WIN32
#include <cstdio>
#include <io.h>
// A double-clicked EXE whose console closes on exit would hide any error text.
// Keep such a window open until Enter is pressed. Scripts and captured runs
// (stdin not a console) never pause.
static void pauseBeforeExit(int code) {
    if(code==0 || _isatty(_fileno(stdin))==0) return;
    std::cout<<"\nPress Enter to close this window...";
    std::cout.flush();
    std::string line; std::getline(std::cin,line);
}
int wmain(int argc, wchar_t** argv) {
    SetConsoleCP(CP_UTF8); SetConsoleOutputCP(CP_UTF8);
    std::vector<std::string> utf8; utf8.reserve(argc);
    for(int i=0;i<argc;++i) {
        int n=WideCharToMultiByte(CP_UTF8,WC_ERR_INVALID_CHARS,argv[i],-1,nullptr,0,nullptr,nullptr);
        if(n<=0) { std::cerr<<"Invalid Unicode command line\n"; pauseBeforeExit(1); return 1; }
        std::string s(static_cast<size_t>(n),'\0');
        WideCharToMultiByte(CP_UTF8,WC_ERR_INVALID_CHARS,argv[i],-1,s.data(),n,nullptr,nullptr);
        s.pop_back(); utf8.push_back(std::move(s));
    }
    std::vector<char*> args; for(auto& s:utf8) args.push_back(s.data());
    int code=appMain(argc,args.data());
    pauseBeforeExit(code);
    return code;
}
#else
int main(int argc, char** argv) { return appMain(argc,argv); }
#endif
