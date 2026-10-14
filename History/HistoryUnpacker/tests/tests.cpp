#include "history.hpp"
#include <chrono>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace history;
static void check(bool value,const char* message) { if(!value) throw std::runtime_error(message); }
template<class F> static void rejects(F f) { bool thrown=false; try { f(); } catch(const std::exception&) { thrown=true; } check(thrown,"Expected rejection"); }
static Bytes unhex(const std::string& s) { Bytes b; for(size_t i=0;i<s.size();i+=2) b.push_back(uint8_t(std::stoul(s.substr(i,2),nullptr,16))); return b; }
static void put32(Bytes& b,uint32_t n) { for(int i=0;i<4;++i) b.push_back(uint8_t(n>>(i*8))); }
int main() {
    fs::path temp=fs::temp_directory_path()/("history-tests-"+std::to_string(std::chrono::high_resolution_clock::now().time_since_epoch().count()));
    try {
        check(nameHash("123456789")==0xcbf43926,"CRC32 known answer");
        check(nameHash("UI\\TEST.PY")==nameHash("ui/test.py"),"Filename normalization");
        auto k=unhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4");
        auto v=unhex("000102030405060708090a0b0c0d0e0f");
        std::array<uint8_t,32> key{}; std::array<uint8_t,16> iv{};
        std::copy(k.begin(),k.end(),key.begin()); std::copy(v.begin(),v.end(),iv.begin());
        auto ciphertext=unhex("dc7e84bfda79164b7ecd8486985d386039ffed143b28b1c832113c6331e5407b");
        auto plaintext=unhex("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e51");
        check(decrypt(ciphertext,key,iv)==plaintext,"NIST SP800-38A CFB128 AES256 vector");
        ciphertext.resize(21); plaintext.resize(21);
        check(decrypt(ciphertext,key,iv)==plaintext,"Partial CFB final block");
        check(lz4(Bytes{0x30,'a','b','c'},3)==Bytes({'a','b','c'}),"LZ4 literals");
        check(lz4(Bytes{0x10,'a',1,0,0x10,'b'},6)==Bytes({'a','a','a','a','a','b'}),"LZ4 overlap");
        rejects([]{lz4(Bytes{0xf0},5);}); rejects([]{lz4(Bytes{0,0,0},4);});
        rejects([]{lz4(Bytes{0x20,'a'},2);}); rejects([]{lz4(Bytes{0x10,'a',2,0},5);});
        rejects([]{lz4(Bytes{0x10,'a'},2);}); rejects([]{lz4(Bytes{0x1f,'a',1,0,255},5);});
        for(const auto& s:{"../x","/root","a/../../x","a:stream","con.txt","a/aux.py","a/x.","a//b","C:\\..\\x"}) rejects([&]{safeRelative(s);});
        check(safeRelative("d:/ymir work/a.dds").generic_string()=="d/ymir work/a.dds","Virtual drive mapping");
        fs::create_directories(temp);
        writeExclusive(temp,"test.txt",Bytes{'a'});
        rejects([&]{writeExclusive(temp,"test.txt",Bytes{'b'});});
        check(readFile(temp/"test.txt")==Bytes{'a'},"No overwrite");
        rejects([&]{readFile(temp/"test.txt",0);});
        Bytes header; put32(header,Magic); header.resize(68,0);
        writeExclusive(temp,"empty.d2",header); Archive empty(temp/"empty.d2"); check(empty.entries.empty(),"Empty valid archive");
        Names names(empty); names.scan(Bytes{'a'});
        header.push_back(1); writeExclusive(temp,"truncated.d2",header);
        rejects([&]{Archive a(temp/"truncated.d2");});
        header.resize(68); put32(header,1); put32(header,0); put32(header,0); put32(header,1); put32(header,0);
        writeExclusive(temp,"bad-offset.d2",header); rejects([&]{Archive a(temp/"bad-offset.d2");});
        header[0]=0; writeExclusive(temp,"wrong-magic.d2",header); rejects([&]{Archive a(temp/"wrong-magic.d2");});
#ifndef _WIN32
        fs::create_directory_symlink(temp,temp/"redirect");
        rejects([&]{writeExclusive(temp/"redirect","blocked.txt",Bytes{1});});
#endif
        fs::remove_all(temp); std::cout<<"All core tests passed.\n"; return 0;
    } catch(const std::exception& e) { fs::remove_all(temp); std::cerr<<e.what()<<'\n'; return 1; }
}
