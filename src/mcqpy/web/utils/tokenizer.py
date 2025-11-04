"""
URL Tokenizer

Simple URL obfuscation system that converts URLs to scrambled tokens
and back. Not cryptographically secure, just makes URLs non-obvious.
"""

import base64
import json
import hashlib
from typing import Optional


class URLTokenizer:
    """Simple URL tokenizer for obfuscation"""
    
    def __init__(self, salt: str = "mcqpy_web_2024"):
        self.salt = salt
        self._setup_cipher()
    
    def _setup_cipher(self):
        """Create a simple character substitution cipher"""
        # Create deterministic shuffled alphabet using salt
        seed_value = int(hashlib.md5(self.salt.encode()).hexdigest(), 16) % (2**32)
        
        self.normal_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_~:/?#[]@!$&'()*+,;="
        
        # Deterministic shuffle using the seed
        chars_list = list(self.normal_chars)
        for i in range(len(chars_list) - 1, 0, -1):
            # Use deterministic "random" based on seed and position
            j = (seed_value + i * 31) % (i + 1)
            chars_list[i], chars_list[j] = chars_list[j], chars_list[i]
        
        self.cipher_chars = ''.join(chars_list)
        
        # Create translation tables
        self.encode_table = str.maketrans(self.normal_chars, self.cipher_chars)
        self.decode_table = str.maketrans(self.cipher_chars, self.normal_chars)
    
    def _get_deterministic_padding(self, url: str) -> str:
        """Generate deterministic padding based on URL"""
        # Use hash of URL to generate consistent padding
        url_hash = hashlib.md5(url.encode()).hexdigest()
        padding_length = (int(url_hash[:2], 16) % 5) + 2  # 2-6 characters
        
        # Generate deterministic padding characters
        padding_chars = []
        for i in range(padding_length):
            char_index = int(url_hash[i*2:(i*2)+2], 16) % 26
            padding_chars.append(chr(ord('a') + char_index))
        
        return ''.join(padding_chars)
    
    def _get_deterministic_affix(self, data: str, options: list) -> str:
        """Get deterministic prefix/suffix based on data"""
        data_hash = hashlib.md5(data.encode()).hexdigest()
        index = int(data_hash[:4], 16) % len(options)
        return options[index]
    
    def create_token(self, url: str) -> str:
        """
        Convert a URL into a scrambled token
        
        Args:
            url: The URL to tokenize
            
        Returns:
            Scrambled token string
        """
        try:
            # Generate deterministic padding
            padding = self._get_deterministic_padding(url)
            
            # Create data structure
            data = {
                'url': url,
                'pad': padding,
                'chk': int(hashlib.md5((url + self.salt).encode()).hexdigest()[:8], 16) % 10000
            }
            
            # Convert to JSON then encode
            json_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
            
            # Apply character substitution
            scrambled = json_str.translate(self.encode_table)
            
            # Base64 encode to make it look more token-like
            encoded = base64.b64encode(scrambled.encode()).decode()
            
            # Add deterministic prefixes/suffixes
            prefixes = ['tk_', 'qt_', 'mx_', 'zq_']
            suffixes = ['_x', '_q', '_m', '_z']
            
            prefix = self._get_deterministic_affix(url + "prefix", prefixes)
            suffix = self._get_deterministic_affix(url + "suffix", suffixes)
            
            token = prefix + encoded + suffix
            
            return token
            
        except Exception as e:
            raise ValueError(f"Failed to create token from URL: {e}")
    
    def decode_token(self, token: str) -> Optional[str]:
        """
        Convert a token back into the original URL
        
        Args:
            token: The token to decode
            
        Returns:
            Original URL or None if invalid token
        """
        try:
            # Remove prefix and suffix
            # Find the base64 part (between first underscore and last underscore)
            parts = token.split('_')
            if len(parts) < 3:
                return None
            
            encoded = '_'.join(parts[1:-1])
            
            # Base64 decode
            try:
                scrambled = base64.b64decode(encoded).decode()
            except Exception:
                return None
            
            # Reverse character substitution
            json_str = scrambled.translate(self.decode_table)
            
            # Parse JSON
            try:
                data = json.loads(json_str)
            except Exception:
                return None
            
            # Validate structure
            if not all(key in data for key in ['url', 'pad', 'chk']):
                return None
            
            url = data['url']
            
            # Verify checksum
            expected_checksum = int(hashlib.md5((url + self.salt).encode()).hexdigest()[:8], 16) % 10000
            if data['chk'] != expected_checksum:
                return None
            
            # Verify padding is deterministic
            expected_padding = self._get_deterministic_padding(url)
            if data['pad'] != expected_padding:
                return None
            
            return url
            
        except Exception:
            return None


# Global tokenizer instance
_tokenizer = URLTokenizer()


def create_token(url: str) -> str:
    """
    Create a token from a URL
    
    Args:
        url: URL to tokenize
        
    Returns:
        Scrambled token
    """
    return _tokenizer.create_token(url)


def decode_token(token: str) -> Optional[str]:
    """
    Decode a token back to the original URL

    Args:
        token: Token to decode

    Returns:
        Original URL or None if invalid
    """
    return _tokenizer.decode_token(token)


# Convenience functions for testing
def test_tokenizer():
    """Test the tokenizer functionality"""
    test_urls = [
        "https://github.com/user/repo/raw/main/manifest.json",
        "https://example.com/quiz/manifest.json",
        "https://raw.githubusercontent.com/test/repo/main/data/quiz_manifest.json"
    ]
    
    print("Testing URL Tokenizer:")
    print("=" * 50)
    
    for url in test_urls:
        # Test multiple times to ensure deterministic behavior
        token1 = create_token(url)
        token2 = create_token(url)
        decoded1 = decode_token(token1)
        decoded2 = decode_token(token2)
        
        print(f"Original:     {url}")
        print(f"Token1:       {token1}")
        print(f"Token2:       {token2}")
        print(f"Same tokens:  {token1 == token2}")
        print(f"Decoded1:     {decoded1}")
        print(f"Decoded2:     {decoded2}")
        print(f"Match:        {url == decoded1 == decoded2}")
        print("-" * 50)


if __name__ == "__main__":
    token = create_token("https://github.com/au-mbg/mcqpy/blob/main/web_quiz/fsb_exam_2024.tar.gz")
    print(token)
    print(decode_token(token))