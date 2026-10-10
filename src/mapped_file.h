// SPDX-License-Identifier: MIT
// Read-only memory mapped file. .epk images can be gigabytes large, so they
// are mapped instead of loaded.
#pragma once

#include <cstddef>
#include <cstdint>
#include <string>

namespace m2 {

class MappedFile {
public:
    MappedFile() = default;
    ~MappedFile();
    MappedFile(const MappedFile&) = delete;
    MappedFile& operator=(const MappedFile&) = delete;
    MappedFile(MappedFile&& other) noexcept;
    MappedFile& operator=(MappedFile&& other) noexcept;

    bool open(const std::string& path, std::string* err = nullptr);
    void close();

    bool isOpen() const { return data_ != nullptr; }
    const uint8_t* data() const { return data_; }
    size_t size() const { return size_; }
    const std::string& path() const { return path_; }

private:
    void reset();

    uint8_t* data_ = nullptr;
    size_t size_ = 0;
    std::string path_;
#ifdef _WIN32
    void* fileHandle_ = nullptr;
    void* mappingHandle_ = nullptr;
#else
    int fd_ = -1;
#endif
};

}  // namespace m2
