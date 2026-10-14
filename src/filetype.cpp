#include "filetype.h"
#include <algorithm>
#include <cctype>
#include <cstring>

namespace UnpackTool {

std::string FileTypeDetector::DetectExtension(const std::vector<uint8_t>& data, const std::string& originalName) {
    return DetectExtension(data.data(), data.size(), originalName);
}

std::string FileTypeDetector::DetectExtension(const uint8_t* data, size_t size, const std::string& originalName) {
    if (size == 0) return ".bin";
    
    // Check for known magic numbers
    if (size >= 4) {
        // DDS
        if (std::memcmp(data, "DDS ", 4) == 0) return ".dds";
        // PNG
        if (size >= 8 && data[0] == 0x89 && data[1] == 'P' && data[2] == 'N' && data[3] == 'G') return ".png";
        // JPG
        if (data[0] == 0xFF && data[1] == 0xD8 && data[2] == 0xFF) return ".jpg";
        // GIF
        if (std::memcmp(data, "GIF8", 4) == 0) return ".gif";
        // BMP
        if (data[0] == 'B' && data[1] == 'M') return ".bmp";
        // TGA - hard to detect, but check footer or header
        // ZIP
        if (data[0] == 'P' && data[1] == 'K' && data[2] == 0x03 && data[3] == 0x04) return ".zip";
        // MCOZ/MCOB etc are already decompressed by now, but check
        if (std::memcmp(data, "MCOZ", 4) == 0 || std::memcmp(data, "MCOB", 4) == 0) return ".mco";
        if (std::memcmp(data, "MCSP", 4) == 0) return ".mcs";
        if (std::memcmp(data, "M2", 2) == 0 && size > 10) {
            // Could be MSA/MSM etc - check ascii
            std::string header((char*)data, std::min<size_t>(size, 16));
            if (header.find("MSA") != std::string::npos) return ".msa";
            if (header.find("MSM") != std::string::npos) return ".msm";
            if (header.find("MSE") != std::string::npos) return ".mse";
        }
    }

    // Check for text-based Metin2 files by content
    std::string start;
    size_t checkLen = std::min<size_t>(size, 2048);
    start.assign((const char*)data, checkLen);

    // Python files
    if (IsPythonFile(data, size)) return ".py";

    // Check for common text patterns
    std::string lower = start;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    // XML-like
    if (start.find("<") != std::string::npos && start.find(">") != std::string::npos) {
        if (lower.find("property") != std::string::npos || lower.find("buildfile") != std::string::npos) return ".xml";
    }

    // MSA/MSM etc often start with ScriptType or version
    if (lower.find("scripttype") != std::string::npos) return ".msa";
    if (lower.find("start_msm") != std::string::npos || lower.find("mesh") != std::string::npos) return ".msm";
    if (lower.find("start_mse") != std::string::npos || lower.find("bounding") != std::string::npos) return ".mse";

    // Check original name hint
    if (!originalName.empty()) {
        size_t dot = originalName.find_last_of('.');
        if (dot != std::string::npos) {
            std::string ext = originalName.substr(dot);
            std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
            // If original had valid extension and file is not .bin, keep it
            if (ext != ".bin" && ext != ".unknown") {
                // If we detected .bin but original has extension, try to keep original unless we have strong detection
                // For now, if we detected .bin, fallback to original
                return ext;
            }
        }
    }

    // Text detection
    if (IsTextFile(data, size)) {
        // Try to guess from path
        if (!originalName.empty()) {
            std::string lowerName = originalName;
            std::transform(lowerName.begin(), lowerName.end(), lowerName.begin(), ::tolower);
            if (lowerName.find(".py") != std::string::npos) return ".py";
            if (lowerName.find(".txt") != std::string::npos) return ".txt";
            if (lowerName.find(".sub") != std::string::npos) return ".sub";
            if (lowerName.find(".msa") != std::string::npos) return ".msa";
            if (lowerName.find(".msm") != std::string::npos) return ".msm";
            if (lowerName.find(".mse") != std::string::npos) return ".mse";
            if (lowerName.find(".msk") != std::string::npos) return ".msk";
            if (lowerName.find(".mot") != std::string::npos) return ".mot";
            if (lowerName.find(".mdatr") != std::string::npos) return ".mdatr";
        }
        return ".txt";
    }

    // Default binary
    // If original name has extension, use it
    if (!originalName.empty()) {
        size_t dot = originalName.find_last_of('.');
        if (dot != std::string::npos && dot + 1 < originalName.size()) {
            std::string ext = originalName.substr(dot);
            if (ext.size() <= 8) return ext;
        }
    }

    return ".bin";
}

bool FileTypeDetector::IsTextFile(const uint8_t* data, size_t size) {
    if (size == 0) return false;
    size_t check = std::min<size_t>(size, 4096);
    size_t nonPrintable = 0;
    for (size_t i = 0; i < check; ++i) {
        uint8_t c = data[i];
        if (c == 0) return false; // null byte -> binary
        if (c < 32 && c != '\n' && c != '\r' && c != '\t') {
            nonPrintable++;
        }
        if (nonPrintable > check / 10) return false;
    }
    return true;
}

bool FileTypeDetector::IsPythonFile(const uint8_t* data, size_t size) {
    if (size == 0) return false;
    std::string start((const char*)data, std::min<size_t>(size, 4096));
    // Common python indicators
    if (start.find("import ") != std::string::npos) return true;
    if (start.find("def ") != std::string::npos && start.find(":") != std::string::npos) return true;
    if (start.find("from ") != std::string::npos && start.find(" import") != std::string::npos) return true;
    if (start.find("class ") != std::string::npos && start.find(":") != std::string::npos) return true;
    if (start.find("print(") != std::string::npos || start.find("print ") != std::string::npos) return true;
    if (start.rfind("#", 0) == 0) { // starts with #
        // Could be python comment, check further
        if (start.find("coding") != std::string::npos || start.find("import") != std::string::npos) return true;
    }
    return false;
}

std::string FileTypeDetector::FixFileName(const std::string& name, const std::vector<uint8_t>& data) {
    std::string ext = DetectExtension(data, name);
    // If name already ends with same ext (case insensitive), keep it
    if (!name.empty()) {
        std::string lowerName = name;
        std::transform(lowerName.begin(), lowerName.end(), lowerName.begin(), ::tolower);
        std::string lowerExt = ext;
        std::transform(lowerExt.begin(), lowerExt.end(), lowerExt.begin(), ::tolower);
        if (lowerName.size() >= lowerExt.size() && lowerName.substr(lowerName.size() - lowerExt.size()) == lowerExt) {
            return name;
        }
        // If name ends with .bin and we detected better extension, replace
        if (lowerName.size() >= 4 && lowerName.substr(lowerName.size() - 4) == ".bin") {
            if (ext != ".bin") {
                return name.substr(0, name.size() - 4) + ext;
            }
        }
        // If name has no extension, add
        if (name.find('.') == std::string::npos) {
            return name + ext;
        }
    }
    return name;
}

} // namespace UnpackTool
