// SPDX-License-Identifier: MIT
#include "mapped_file.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

#include <utility>

namespace m2 {

MappedFile::~MappedFile() { reset(); }

MappedFile::MappedFile(MappedFile&& other) noexcept
    : data_(other.data_), size_(other.size_), path_(std::move(other.path_))
#ifdef _WIN32
      ,
      fileHandle_(other.fileHandle_), mappingHandle_(other.mappingHandle_)
#else
      ,
      fd_(other.fd_)
#endif
{
    other.data_ = nullptr;
    other.size_ = 0;
#ifdef _WIN32
    other.fileHandle_ = nullptr;
    other.mappingHandle_ = nullptr;
#else
    other.fd_ = -1;
#endif
}

MappedFile& MappedFile::operator=(MappedFile&& other) noexcept {
    if (this != &other) {
        reset();
        data_ = other.data_;
        size_ = other.size_;
        path_ = std::move(other.path_);
#ifdef _WIN32
        fileHandle_ = other.fileHandle_;
        mappingHandle_ = other.mappingHandle_;
        other.fileHandle_ = nullptr;
        other.mappingHandle_ = nullptr;
#else
        fd_ = other.fd_;
        other.fd_ = -1;
#endif
        other.data_ = nullptr;
        other.size_ = 0;
    }
    return *this;
}

void MappedFile::reset() {
#ifdef _WIN32
    if (data_) ::UnmapViewOfFile(data_);
    if (mappingHandle_) ::CloseHandle(mappingHandle_);
    if (fileHandle_) ::CloseHandle(fileHandle_);
    mappingHandle_ = nullptr;
    fileHandle_ = nullptr;
#else
    if (data_ && size_) ::munmap(data_, size_);
    if (fd_ >= 0) ::close(fd_);
    fd_ = -1;
#endif
    data_ = nullptr;
    size_ = 0;
}

void MappedFile::close() { reset(); }

bool MappedFile::open(const std::string& path, std::string* err) {
    reset();
    auto fail = [&](const std::string& m) {
        if (err) *err = m;
        return false;
    };
#ifdef _WIN32
    HANDLE h = ::CreateFileA(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING,
                             FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return fail("cannot open " + path);
    LARGE_INTEGER li;
    if (!::GetFileSizeEx(h, &li)) {
        ::CloseHandle(h);
        return fail("cannot stat " + path);
    }
    if (li.QuadPart == 0) {
        ::CloseHandle(h);
        data_ = nullptr;
        size_ = 0;
        path_ = path;
        return true;
    }
    HANDLE map = ::CreateFileMappingA(h, nullptr, PAGE_READONLY, 0, 0, nullptr);
    if (!map) {
        ::CloseHandle(h);
        return fail("cannot map " + path);
    }
    void* view = ::MapViewOfFile(map, FILE_MAP_READ, 0, 0, 0);
    if (!view) {
        ::CloseHandle(map);
        ::CloseHandle(h);
        return fail("cannot map view of " + path);
    }
    fileHandle_ = h;
    mappingHandle_ = map;
    data_ = static_cast<uint8_t*>(view);
    size_ = static_cast<size_t>(li.QuadPart);
    path_ = path;
    return true;
#else
    int fd = ::open(path.c_str(), O_RDONLY);
    if (fd < 0) return fail("cannot open " + path);
    struct stat st {};
    if (::fstat(fd, &st) != 0) {
        ::close(fd);
        return fail("cannot stat " + path);
    }
    if (st.st_size == 0) {
        ::close(fd);
        fd_ = -1;
        data_ = nullptr;
        size_ = 0;
        path_ = path;
        return true;
    }
    void* view = ::mmap(nullptr, static_cast<size_t>(st.st_size), PROT_READ, MAP_PRIVATE, fd, 0);
    if (view == MAP_FAILED) {
        ::close(fd);
        return fail("mmap failed for " + path);
    }
    fd_ = fd;
    data_ = static_cast<uint8_t*>(view);
    size_ = static_cast<size_t>(st.st_size);
    path_ = path;
    return true;
#endif
}

}  // namespace m2
