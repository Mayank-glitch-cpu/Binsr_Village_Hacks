#!/usr/bin/env python3
"""
Simple HTTP server for TREC Report Generator
Run this script to serve the files locally and avoid CORS issues.
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to project root directory (parent of src/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from src/
    os.chdir(project_root)
    
    Handler = MyHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("=" * 60)
            print("TREC Report Generator Server")
            print("=" * 60)
            print(f"Server running at: http://localhost:{PORT}")
            print(f"Open your browser to: http://localhost:{PORT}/index.html")
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}/index.html')
            except:
                pass
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

if __name__ == "__main__":
    main()
