# HAVE ACCESS NOW?

> **Automated 403 Forbidden Bypass Tool** - Test 1000+ bypass techniques to bypass 403 errors

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-d0x-red.svg)](https://github.com/d0xng)

---

## Overview

**HAVE ACCESS NOW?** is a powerful automated tool designed to test and bypass 403 Forbidden errors on web endpoints. It systematically tests over **1000+ different bypass techniques** including URL encoding, path manipulation, HTTP methods, headers, and more.

### Features

- **1000+ Bypass Techniques** - Comprehensive collection of bypass methods
- **Nuclei-style Output** - Clean, color-coded results
- **Smart Detection** - Automatically highlights successful bypasses (200 OK) and different status codes
- **Rate Limiting Protection** - Built-in 3-second delay between requests
- **False Positive Detection** - Filters out path traversals that go to root instead of bypassing
- **Detailed Reporting** - Shows status codes, response sizes, and techniques used

---

## Installation

### Requirements

```bash
pip install requests colorama
```

---

## Usage

### Basic Usage

```bash
python bypasser.py <URL>
```

### Example

```bash
python bypasser.py https://example.com/api/admin
```

---

## Tested Techniques

### URL Encoding Bypasses
- Single encoding (`%26`, `%2F`, `%3F`, etc.)
- Double encoding (`%2526`, `%252F`, etc.)
- Extended encoding (200+ variations)

### Path Manipulation
- Trailing slashes (`/`, `//`, `///`)
- Path traversal (`../`, `..%2F`, `%2e%2e%2f`)
- Semicolon variations (`;`, `..;`, `..;/`)
- Special characters (`?`, `#`, `&`, `,`)

### Path Permutations
- Payload insertion at all path positions
- Before/after/inside path segments
- Multiple payload combinations

### HTTP Methods
- `GET`, `HEAD`, `POST`, `PUT`, `DELETE`, `PATCH`
- `OPTIONS`, `TRACE`, `CONNECT`, `TRACK`
- `UPDATE`, `LOCK`, `COPY`, `MOVE`, and more

### Header Bypasses
- IP Spoofing (50+ headers)
- Path Override headers
- Host manipulation
- Protocol/Port headers

### Case Variations
- Uppercase, lowercase, swapcase
- Mixed case combinations

### Endpath & Midpath Payloads
- 50+ endpath payloads
- 200+ midpath payloads
- Complex combinations

---

## Output Format

The tool displays results in Nuclei-style format:

```
[BYPASSED] [403-bypass] https://example.com/api/admin..; - Path permutation [200] [1234 bytes]
  technique: path-permutation
  payload: ..;

[DIFFERENT STATUS] [403-bypass] https://example.com/api/admin%26 - URL encoding [400] [567 bytes]
  technique: url-encoding
  payload: %26

[NOT BYPASSED] [403-bypass] https://example.com/api/admin - Original request [403] [162 bytes]
```

### Status Indicators

- **[BYPASSED]** (Green) - Successful bypass with status 200
- **[DIFFERENT STATUS]** (Red) - Status code changed (not 200, not 403)
- **[NOT BYPASSED]** (Red) - Still returns 403 or original status

---

## Configuration

### Delay Between Requests

The tool includes a **3-second delay** between each request to avoid rate limiting and blocking. This ensures safe testing while maintaining thorough coverage.

### False Positive Detection

The tool automatically filters out path traversals that are likely false positives (e.g., going to root directory instead of actually bypassing the 403). This helps focus on real bypasses.

---

## Statistics

- **18 HTTP Methods** tested
- **50+ Headers** with multiple IP variations
- **250+ URL Encoding** payloads
- **200+ Midpath** payloads
- **50+ Endpath** payloads
- **Path Permutations** in all possible positions
- **Total: 1000+ bypass techniques**

---

## Keyboard Interrupt

Press `Ctrl+C` to gracefully stop the tool. You'll see a friendly message instead of a traceback.

---

## Disclaimer

This tool is for **authorized security testing only**. Only use it on systems you own or have explicit permission to test. Unauthorized access attempts are illegal.

---

## Author

**Created by d0x**

- GitHub: [@d0xng](https://github.com/d0xng)

---

## License

This project is licensed under the MIT License.

---

## Contributing

Contributions, issues, and feature requests are welcome!

---

## Show Your Support

If you find this tool useful, give it a star on GitHub!

---

**Happy Hacking!**
