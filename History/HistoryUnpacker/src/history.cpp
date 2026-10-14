#include "history.hpp"
#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cwctype>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
extern "C" {
#include "aes.h"
}
#define XXH_INLINE_ALL
#include "xxhash.h"
namespace history {
static void require(bool ok, const std::string& message) { if (!ok) throw std::runtime_error(message); }
static uint32_t u32(const uint8_t* p) {
    return uint32_t(p[0]) | uint32_t(p[1])<<8 | uint32_t(p[2])<<16 | uint32_t(p[3])<<24;
}
Bytes readFile(const fs::path& path, size_t limit) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    require(bool(f), "Cannot open: " + path.string());
    auto size = f.tellg();
    require(size >= 0 && uint64_t(size) <= limit, "File exceeds configured limit: " + path.string());
    Bytes b(static_cast<size_t>(size)); f.seekg(0);
    if (!b.empty()) f.read(reinterpret_cast<char*>(b.data()), static_cast<std::streamsize>(b.size()));
    require(bool(f), "Read failed: " + path.string()); return b;
}
std::string normalize(std::string s) {
    for (char& c:s) { if(c=='\\') c='/'; if(c>='A' && c<='Z') c=char(c-'A'+'a'); } return s;
}
uint32_t nameHash(const std::string& s) {
    uint32_t crc=0xffffffff;
    for (unsigned char c:normalize(s)) {
        crc ^= c;
        for(int i=0;i<8;++i) crc=(crc>>1) ^ (0xedb88320u & (0u-(crc&1u)));
    }
    return ~crc;
}
std::string hex32(uint32_t n) { std::ostringstream s; s<<std::hex<<std::setfill('0')<<std::setw(8)<<n; return s.str(); }
Bytes decrypt(const Bytes& in, const std::array<uint8_t,32>& key, const std::array<uint8_t,16>& iv) {
    AES_ctx ctx{}; AES_init_ctx(&ctx,key.data());
    auto feedback=iv; Bytes out(in.size());
    for(size_t pos=0;pos<in.size();pos+=16) {
        auto stream=feedback; AES_ECB_encrypt(&ctx,stream.data());
        size_t count=std::min(size_t(16),in.size()-pos);
        for(size_t j=0;j<count;++j) { out[pos+j]=in[pos+j]^stream[j]; feedback[j]=in[pos+j]; }
    }
    return out;
}
// Bounded raw LZ4 block decoder, including overlapping matches.
Bytes lz4(const Bytes& in, size_t size) {
    require(size<=MaxFile,"Uncompressed size exceeds limit");
    Bytes out; out.reserve(size); size_t pos=0;
    auto length=[&](size_t n) {
        if(n==15) { uint8_t b; do {
            require(pos<in.size(),"Truncated LZ4 length"); b=in[pos++];
            require(n<=size && b<=size-n,"LZ4 length exceeds output"); n+=b;
        } while(b==255); } return n;
    };
    while(pos<in.size()) {
        uint8_t token=in[pos++]; size_t literals=length(token>>4);
        require(literals<=in.size()-pos && literals<=size-out.size(),"Invalid LZ4 literals");
        out.insert(out.end(),in.begin()+pos,in.begin()+pos+literals); pos+=literals;
        if(pos==in.size()) break;
        require(in.size()-pos>=2,"Truncated LZ4 offset");
        size_t distance=in[pos] | size_t(in[pos+1])<<8; pos+=2;
        require(distance>0 && distance<=out.size(),"Invalid LZ4 back-reference");
        size_t count=length(token&15)+4;
        require(count<=size-out.size(),"LZ4 match exceeds output");
        for(size_t j=0;j<count;++j) out.push_back(out[out.size()-distance]);
    }
    require(out.size()==size,"LZ4 size mismatch"); return out;
}
Archive::Archive(const fs::path& path):path_(path) {
    std::ifstream f(path,std::ios::binary);
    require(bool(f),"Cannot open archive: "+path.string());
    uint64_t total=fs::file_size(path);
    require(total>=68 && total<=UINT32_MAX,"Unsupported archive size");
    std::array<uint8_t,68> h{}; f.read(reinterpret_cast<char*>(h.data()),h.size());
    require(bool(f) && u32(h.data())==Magic,"Not a supported History D2 archive (Alt2 is not supported)");
    std::copy_n(h.begin()+4,32,key.begin()); std::copy_n(h.begin()+36,16,iv.begin());
    uint64_t pos=68; std::set<uint32_t> seen;
    while(pos<total) {
        require(total-pos>=20,"Truncated entry header");
        std::array<uint8_t,20> b{}; f.seekg(static_cast<std::streamoff>(pos)); f.read(reinterpret_cast<char*>(b.data()),20);
        require(bool(f),"Entry read failed");
        Entry e{u32(b.data()),u32(b.data()+4),u32(b.data()+8),u32(b.data()+12),u32(b.data()+16)};
        require(e.offset==pos+20 && e.stored<=total-e.offset,"Invalid entry offset or size");
        require(e.size<=MaxFile && e.stored<=MaxFile,"Entry exceeds 256 MiB safety limit");
        require(seen.insert(e.hash).second,"Duplicate name hash: "+hex32(e.hash));
        require(entries.size()<1000000,"Too many entries");
        entries.push_back(e); pos=uint64_t(e.offset)+e.stored;
    }
}
Bytes Archive::decode(const Entry& e) const {
    std::ifstream f(path_,std::ios::binary); f.seekg(e.offset);
    Bytes raw(e.stored); if(!raw.empty()) f.read(reinterpret_cast<char*>(raw.data()),raw.size());
    require(bool(f),"Payload read failed");
    auto data=decrypt(raw,key,iv); if(e.stored!=e.size) data=lz4(data,e.size);
    require(XXH32(data.data(),data.size(),Magic)==e.checksum,
        "Checksum mismatch for "+hex32(e.hash)+" (wrong key, corrupt data, or unsupported History variant)");
    return data;
}
Names::Names(const Archive& a) { for(const auto& e:a.entries) wanted_.insert(e.hash); }
void Names::add(std::string name) {
    name=normalize(name);
    if(name.empty() || name.size()>1024) return;
    auto h=nameHash(name); if(wanted_.count(h)) names_[h].insert(name);
}
void Names::scan(const Bytes& data) {
    // References and Python import identifiers are candidates, never accepted without CRC equality.
    auto consider=[&](const std::string& s) {
        if(s.size()<2 || s.size()>512) return;
        add(s); add(s+".py"); add("uiscript/"+s+".py");
        std::string module=s; std::replace(module.begin(),module.end(),'.','/'); add(module+".py");
    };
    std::string token;
    for(uint8_t c:data) {
        bool valid=(c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_'||c=='.'||c=='/'||c=='\\'||c==':'||c=='-';
        if(valid) { if(token.size()<2048) token+=char(c); }
        else { consider(token); token.clear(); }
    }
    consider(token);
    // UTF-16LE references from the Windows executable.
    for(size_t parity=0;parity<2;++parity) {
        token.clear();
        for(size_t i=parity;i+1<data.size();i+=2) {
            uint8_t c=data[i];
            if(data[i+1]==0 && c>=32 && c<127) { if(token.size()<2048) token+=char(c); }
            else { consider(token); token.clear(); }
        }
        consider(token);
    }
}
void Names::load(const fs::path& path) {
    auto b=readFile(path,16*1024*1024); std::istringstream in(std::string(b.begin(),b.end())); std::string line;
    while(std::getline(in,line)) { if(!line.empty() && line.back()=='\r') line.pop_back(); if(!line.empty() && line[0]!='#') add(line); }
}
std::string Names::get(uint32_t hash) const {
    auto it=names_.find(hash); return it!=names_.end() && it->second.size()==1 ? *it->second.begin() : "";
}
size_t Names::resolved() const { size_t n=0; for(const auto& p:names_) if(p.second.size()==1) ++n; return n; }
fs::path safeRelative(std::string name) {
    name=normalize(name);
    // Preserve Metin2 virtual drive paths under a relative drive folder.
    if(name.size()>3 && name[0]>='a' && name[0]<='z' && name.substr(1,2)==":/") name.erase(1,1);
    require(!name.empty() && name[0]!='/',"Absolute or empty output name rejected");
    fs::path result; std::istringstream stream(name); std::string part;
    while(std::getline(stream,part,'/')) {
        require(!part.empty() && part!="." && part!="..","Unsafe path component");
        require(part.back()!='.' && part.back()!=' ',"Unsafe Windows filename suffix");
        for(unsigned char c:part) require(c>=32 && std::string(":*?\"<>|").find(char(c))==std::string::npos,"Invalid Windows filename");
        auto stem=part.substr(0,part.find('.'));
        require(stem!="con" && stem!="prn" && stem!="aux" && stem!="nul" &&
            !(stem.size()==4 && (stem.substr(0,3)=="com" || stem.substr(0,3)=="lpt") && stem[3]>='0' && stem[3]<='9'),"Reserved Windows filename");
        result/=fs::u8path(part);
    }
    require(!result.empty(),"Empty output path"); return result;
}
// Windows file names are case-insensitive, and weakly_canonical() returns the on-disk casing,
// which may differ from the spelling the user typed. Compare folded spellings there.
static bool sameSpelling(const fs::path& a, const fs::path& b) {
#ifdef _WIN32
    auto fold=[](std::wstring s) { for(auto& c:s) c=static_cast<wchar_t>(std::towlower(c)); return s; };
    return fold(a.wstring())==fold(b.wstring());
#else
    return a==b;
#endif
}
void writeExclusive(const fs::path& root, const fs::path& relative, const Bytes& data) {
    require(!relative.is_absolute(),"Absolute output rejected");
    for(const auto& part:relative) require(part!="..", "Output traversal rejected");
    fs::path target=fs::absolute(root/relative).lexically_normal();
    // Do not follow existing symlinks/junction-like redirected paths.
    fs::path current;
    for(const auto& part:target.parent_path()) {
        current/=part;
        // A bare drive prefix ("C:") or root ("C:\", "/") is not a directory to create or
        // inspect. Calling weakly_canonical("C:") resolves it against the drive's current
        // directory on Windows, which made every output on Windows fail this check.
        if(!current.has_relative_path()) continue;
        auto status=fs::symlink_status(current);
        require(!fs::is_symlink(status),"Symlink output directory rejected");
        if(fs::exists(status)) require(fs::is_directory(status),"Output parent is not a directory");
        else fs::create_directory(current);
        require(sameSpelling(fs::weakly_canonical(current),current.lexically_normal()),"Redirected output directory rejected");
    }
    require(!fs::exists(fs::symlink_status(target)),"Output already exists: "+target.string());
    // C11 'x' performs exclusive creation, preventing accidental replacement.
#ifdef _WIN32
    FILE* file=nullptr; _wfopen_s(&file,target.c_str(),L"wbx");
#else
    FILE* file=std::fopen(target.c_str(),"wbx");
#endif
    require(file!=nullptr,"Cannot create output exclusively: "+target.string());
    bool ok=data.empty() || std::fwrite(data.data(),1,data.size(),file)==data.size();
    if(std::fclose(file)!=0) ok=false;
    if(!ok) { std::error_code ec; fs::remove(target,ec); throw std::runtime_error("Output write failed"); }
}
bool isHistoryArchive(const fs::path& path) {
    std::error_code ec;
    if(!fs::is_regular_file(path,ec)) return false;
    std::ifstream f(path,std::ios::binary);
    if(!f) return false;
    uint8_t magic[4]={};
    f.read(reinterpret_cast<char*>(magic),4);
    return f.gcount()==4 && u32(magic)==Magic;
}
bool hasArchiveName(const fs::path& path) {
    auto extension=path.extension().string();
    for(auto& c:extension) c=char(std::tolower(static_cast<unsigned char>(c)));
    if(extension==".d2") return true;
    // Metin2-style virtual-filesystem packs often have no extension at all.
    if(!extension.empty()) return false;
    auto stem=normalize(path.filename().string());
    static const char* const known[]={"root","index","locale","map","sound","effect",
                                      "npc","item","guild","season","dungeon","pack"};
    for(const char* name:known) if(stem==name) return true;
    return false;
}
static void collectFromDirectory(const fs::path& directory,std::vector<fs::path>& out,std::set<fs::path>& seen) {
    std::error_code ec;
    if(!fs::is_directory(directory,ec)) return;
    for(auto it=fs::recursive_directory_iterator(directory,fs::directory_options::skip_permission_denied,ec);
        it!=fs::recursive_directory_iterator();it.increment(ec)) {
        if(ec) { ec.clear(); it.disable_recursion_pending(); continue; }
        if(it.depth()>SearchDepth) { it.disable_recursion_pending(); continue; }
        if(!it->is_regular_file(ec) || ec) continue;
        if(!hasArchiveName(it->path()) || !isHistoryArchive(it->path())) continue;
        auto absolute=fs::absolute(it->path()).lexically_normal();
        if(seen.insert(absolute).second) out.push_back(it->path());
    }
}
std::vector<fs::path> collectArchives(const fs::path& directory) {
    std::vector<fs::path> out; std::set<fs::path> seen;
    collectFromDirectory(directory/"pack",out,seen);
    collectFromDirectory(directory,out,seen);
    std::sort(out.begin(),out.end(),[](const fs::path& a,const fs::path& b) {
        // Keep the historical primary archive first; everything else stays alphabetical.
        auto primary=[](const fs::path& p) { return normalize(p.filename().string())=="workplace.d2" ? 0 : 1; };
        int rank=primary(a)-primary(b);
        return rank!=0 ? rank<0 : a.string()<b.string();
    });
    return out;
}
std::vector<fs::path> resolveArchiveArgument(const fs::path& path) {
    std::error_code ec;
    if(fs::is_directory(path,ec)) {
        auto found=collectArchives(path);
        require(!found.empty(),"No History D2 archive found in directory: "+path.string());
        return found;
    }
    require(fs::is_regular_file(path,ec),"Cannot open archive: "+path.string());
    require(isHistoryArchive(path),"Not a supported History D2 archive (Alt2 is not supported): "+path.string());
    return {path};
}
void discoverAssets(const fs::path& start,std::vector<fs::path>& archives,fs::path& exe,fs::path& bundledNames,int levels) {
    std::error_code ec;
    auto p=fs::absolute(start,ec).lexically_normal();
    if(ec) p=start;
    std::set<fs::path> seen;
    for(const auto& existing:archives) seen.insert(fs::absolute(existing).lexically_normal());
    auto addArchives=[&](const fs::path& directory) {
        for(auto& found:collectArchives(directory)) {
            auto absolute=fs::absolute(found).lexically_normal();
            if(seen.insert(absolute).second) archives.push_back(found);
        }
    };
    for(int i=0;i<levels;++i) {
        for(const auto& root:{p,p/"History"}) {
            addArchives(root/"pack");
            addArchives(root);
            if(exe.empty() && fs::is_regular_file(root/"History2.exe",ec)) exe=root/"History2.exe";
            for(const auto& f:{root/"data/history-names.txt",root/"HistoryUnpacker/data/history-names.txt"})
                if(bundledNames.empty() && fs::is_regular_file(f,ec)) bundledNames=f;
        }
        if(p==p.parent_path()) break;
        p=p.parent_path();
    }
}
}
