#include "history.hpp"
#include <algorithm>
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
    fs::path archive, exe, names, out="History-output";
    bool unresolved=false;
};
static std::string quote(const std::string& s) {
    std::string r="\""; for(char c:s) { if(c=='"') r+='"'; r+=c; } return r+'"';
}
static Bytes bytes(const std::string& s) { return Bytes(s.begin(),s.end()); }
static void usage() {
    std::cout<<R"(History Unpacker - History D2 only
Usage: HistoryUnpacker [options] [command] [argument]
Commands:
  menu                 Interactive English menu (default)
  info                 Inspect archive format and entry sizes
  keys                 Extract header key/IV and validate against a payload
  list                 Recover and list names; unresolved names remain explicit
  verify               Decrypt, decompress and verify every entry (no output files)
  extract NAME         Extract one entry by original virtual filename
  all                  Extract all resolved files; skip unresolved by default
  manifest FILE.csv    Export entry metadata and recovered-name mapping
Options:
  --archive FILE       History archive, regardless of its extension
  --exe FILE           Read executable references for name recovery; never execute it
  --names FILE         Additional names, one original virtual path per line
  --out DIRECTORY      Extraction destination (default: History-output)
  --include-unresolved Export unknown names as _unresolved/HASH.unresolved
  --help               Show this help
Existing files are never overwritten. No type/extension whitelist is applied.
A CRC32 filename hash is not reversible; names are recovered from candidates.
)";
}
static void recover(Names& names, const Archive& archive, const Config& c, const fs::path& bundled) {
    if(!bundled.empty()) names.load(bundled);
    if(!c.names.empty()) names.load(c.names);
    if(!c.exe.empty()) {
        auto b=readFile(c.exe);
        if(b.size()<64 || b[0]!='M' || b[1]!='Z') throw std::runtime_error("Executable is not a PE/MZ file");
        names.scan(b);
    }
    size_t failed=0;
    for(const auto& e:archive.entries) {
        try { names.scan(archive.decode(e)); }
        catch(const std::exception&) { ++failed; }
    }
    std::cout<<"Recovered "<<names.resolved()<<" / "<<archive.entries.size()<<" names from CRC-matched references.\n";
    if(failed) std::cout<<"Warning: "<<failed<<" payloads could not be scanned. Run verify for details.\n";
}
static int run(const std::string& command, const std::string& arg, const Config& c, const fs::path& bundled) {
    Archive a(c.archive);
    if(command=="info") {
        uint64_t raw=0,stored=0; for(const auto& e:a.entries) { raw+=e.size; stored+=e.stored; }
        std::cout<<"Archive: "<<c.archive.string()<<"\nFormat: History D2 / F00FED5C\n"
                 <<"Cipher: AES-256-CFB128 (reset IV per entry)\nCompression: raw LZ4\n"
                 <<"Integrity: XXH32, seed F00FED5C\nNames: CRC32, lowercase / separators\n"
                 <<"Entries: "<<a.entries.size()<<"\nStored bytes: "<<stored<<"\nDecoded bytes: "<<raw<<"\n";
        return 0;
    }
    if(command=="keys") {
        if(a.entries.empty()) throw std::runtime_error("Empty archive: key cannot be validated");
        a.decode(a.entries.front());
        auto hex=[](const auto& data) { const char* h="0123456789abcdef"; for(uint8_t b:data) std::cout<<h[b>>4]<<h[b&15]; std::cout<<'\n'; };
        std::cout<<"Key source: archive header, not a guessed EXE byte sequence.\n"
                 <<"Validated with first entry's decompression and XXH32 checksum.\nAES-256 key: "; hex(a.key);
        std::cout<<"CFB128 IV: "; hex(a.iv);
        std::cout<<"This History profile needs no executable XOR mask. Other variants may differ.\n"; return 0;
    }
    if(command=="verify") {
        size_t good=0,failed=0;
        for(const auto& e:a.entries) {
            try { a.decode(e); ++good; }
            catch(const std::exception& ex) { ++failed; std::cerr<<hex32(e.hash)<<": "<<ex.what()<<'\n'; }
        }
        std::cout<<"Verified: "<<good<<"; failed: "<<failed<<"; total: "<<a.entries.size()<<'\n'; return failed?1:0;
    }
    if(command=="extract") {
        if(arg.empty()) throw std::runtime_error("An original filename is required");
        auto h=nameHash(arg); auto it=std::find_if(a.entries.begin(),a.entries.end(),[&](const Entry& e){return e.hash==h;});
        if(it==a.entries.end()) throw std::runtime_error("Filename not found (CRC32 "+hex32(h)+")");
        auto rel=safeRelative(arg); writeExclusive(c.out,rel,a.decode(*it));
        std::cout<<"Extracted: "<<(c.out/rel).string()<<" (content checksum verified)\n"; return 0;
    }
    if(command!="list" && command!="manifest" && command!="all") throw std::runtime_error("Unknown command: "+command);
    Names names(a); recover(names,a,c,bundled);
    if(command=="list") {
        for(const auto& e:a.entries) { auto n=names.get(e.hash); std::cout<<hex32(e.hash)<<'\t'<<e.size<<'\t'<<(n.empty()?"[unresolved or ambiguous]":n)<<'\n'; }
        return 0;
    }
    std::ostringstream report;
    report<<"name_crc32,original_candidate,output_path,decoded_size,stored_size,xxh32,status,detail\n";
    size_t done=0,skipped=0,failed=0;
    if(command=="manifest" && arg.empty()) throw std::runtime_error("Manifest path is required");
    fs::path reportPath=command=="all" ? c.out/"history-manifest.csv" : fs::u8path(arg);
    if(fs::exists(fs::symlink_status(reportPath))) throw std::runtime_error("Manifest already exists; choose a fresh output directory/path");
    for(const auto& e:a.entries) {
        std::string name=names.get(e.hash),destination,status,detail;
        if(command=="manifest") status=name.empty()?"unresolved_or_ambiguous":"crc_matched_candidate";
        else if(name.empty() && !c.unresolved) { status="skipped_unresolved"; ++skipped; }
        else {
            try {
                auto rel=name.empty()? fs::path("_unresolved")/(hex32(e.hash)+".unresolved") : safeRelative(name);
                destination=rel.generic_u8string();
                writeExclusive(c.out,rel,a.decode(e)); status=name.empty()?"verified_unresolved":"verified_extracted"; ++done;
            } catch(const std::exception& ex) { status="failed"; detail=ex.what(); ++failed; std::cerr<<hex32(e.hash)<<": "<<detail<<'\n'; }
        }
        report<<hex32(e.hash)<<','<<quote(name)<<','<<quote(destination)<<','<<e.size<<','<<e.stored<<','<<hex32(e.checksum)<<','<<status<<','<<quote(detail)<<'\n';
    }
    writeExclusive(reportPath.has_parent_path()?reportPath.parent_path():fs::path("."),reportPath.filename(),bytes(report.str()));
    std::cout<<"Manifest: "<<reportPath.string()<<'\n';
    if(command=="all") std::cout<<"Extracted: "<<done<<"; unresolved skipped: "<<skipped<<"; failed: "<<failed<<'\n';
    return failed?1:(skipped?2:0);
}
static std::string prompt(const std::string& text) {
    std::cout<<text; std::string line;
    if(!std::getline(std::cin,line)) throw std::runtime_error("Input closed");
    if(line.size()>=2 && line.front()=='"' && line.back()=='"') line=line.substr(1,line.size()-2);
    return line;
}
static int menu(Config c, const fs::path& bundled) {
    while(true) {
        std::cout<<"\n=== History Unpacker ===\nArchive: "<<c.archive.string()<<"\nOutput: "<<c.out.string()
        <<"\n1. Inspect archive\n2. Extract and validate key / IV\n3. Recover and list filenames\n"
        <<"4. Decrypt one file by name\n5. Decrypt all files\n6. Verify all payloads\n7. Export filename manifest\n"
        <<"8. Change archive / output paths\n9. Set executable / additional name list\n"
        <<"10. Toggle unresolved export (currently "<<(c.unresolved?"ON":"OFF")<<")\n0. Exit\n";
        std::string choice; std::cout<<"> "; if(!std::getline(std::cin,choice)||choice=="0") return 0;
        try {
            if(choice=="1") run("info","",c,bundled);
            else if(choice=="2") run("keys","",c,bundled);
            else if(choice=="3") run("list","",c,bundled);
            else if(choice=="4") run("extract",prompt("Original virtual filename: "),c,bundled);
            else if(choice=="5") run("all","",c,bundled);
            else if(choice=="6") run("verify","",c,bundled);
            else if(choice=="7") run("manifest",prompt("New manifest CSV path: "),c,bundled);
            else if(choice=="8") { c.archive=fs::u8path(prompt("Archive path: ")); c.out=fs::u8path(prompt("Output directory: ")); }
            else if(choice=="9") { c.exe=fs::u8path(prompt("History executable (blank = none): ")); c.names=fs::u8path(prompt("Extra name list (blank = none): ")); }
            else if(choice=="10") c.unresolved=!c.unresolved;
            else std::cout<<"Unknown selection.\n";
        } catch(const std::exception& ex) { std::cerr<<"Error: "<<ex.what()<<'\n'; }
    }
}
static int appMain(int argc,char** argv) {
    try {
        Config c; fs::path bundled;
        // Locate assets from working directory or next to the built executable.
        for(auto start:{fs::current_path(),fs::absolute(fs::u8path(argv[0])).parent_path()}) {
            auto p=start;
            for(int i=0;i<7;++i) {
                for(const auto& root:{p,p/"History"}) {
                    if(c.archive.empty() && fs::exists(root/"pack/workplace.d2")) c.archive=root/"pack/workplace.d2";
                    if(c.exe.empty() && fs::exists(root/"History2.exe")) c.exe=root/"History2.exe";
                    for(const auto& f:{root/"data/history-names.txt",root/"HistoryUnpacker/data/history-names.txt"})
                        if(bundled.empty() && fs::exists(f)) bundled=f;
                }
                if(p==p.parent_path()) break;
                p=p.parent_path();
            }
        }
        std::string command="menu",arg; bool haveCommand=false;
        for(int i=1;i<argc;++i) {
            std::string v=argv[i];
            if(v=="--help") { usage(); return 0; }
            if(v=="--include-unresolved") { c.unresolved=true; continue; }
            if(v=="--archive" || v=="--exe" || v=="--names" || v=="--out") {
                if(++i>=argc) throw std::runtime_error("Missing option value: "+v);
                auto path=fs::u8path(argv[i]);
                if(v=="--archive") c.archive=path; else if(v=="--exe") c.exe=path;
                else if(v=="--names") c.names=path; else c.out=path;
            } else if(v.rfind("--",0)==0) throw std::runtime_error("Unknown option: "+v);
            else if(!haveCommand) { command=v; haveCommand=true; }
            else if(arg.empty()) arg=v;
            else throw std::runtime_error("Too many arguments; quote paths containing spaces");
        }
        if(command=="menu") return menu(c,bundled);
        if(c.archive.empty()) throw std::runtime_error("Specify --archive FILE");
        return run(command,arg,c,bundled);
    } catch(const std::exception& ex) { std::cerr<<"Error: "<<ex.what()<<'\n'; return 1; }
}

#ifdef _WIN32
int wmain(int argc, wchar_t** argv) {
    SetConsoleCP(CP_UTF8); SetConsoleOutputCP(CP_UTF8);
    std::vector<std::string> utf8; utf8.reserve(argc);
    for(int i=0;i<argc;++i) {
        int n=WideCharToMultiByte(CP_UTF8,WC_ERR_INVALID_CHARS,argv[i],-1,nullptr,0,nullptr,nullptr);
        if(n<=0) { std::cerr<<"Invalid Unicode command line\n"; return 1; }
        std::string s(static_cast<size_t>(n),'\0');
        WideCharToMultiByte(CP_UTF8,WC_ERR_INVALID_CHARS,argv[i],-1,s.data(),n,nullptr,nullptr);
        s.pop_back(); utf8.push_back(std::move(s));
    }
    std::vector<char*> args; for(auto& s:utf8) args.push_back(s.data());
    return appMain(argc,args.data());
}
#else
int main(int argc, char** argv) { return appMain(argc,argv); }
#endif
