#pragma once
#include <string>
#include <vector>
#include <cstdint>

namespace UnpackTool {

class FileTypeDetector {
public:
    static std::string DetectExtension(const std::vector<uint8_t>& data, const std::string& originalName = "");
    static std::string DetectExtension(const uint8_t* data, size_t size, const std::string& originalName = "");
    static bool IsTextFile(const uint8_t* data, size_t size);
    static bool IsPythonFile(const uint8_t* data, size_t size);
    static std::string FixFileName(const std::string& name, const std::vector<uint8_t>& data);
};

} // namespace UnpackTool
