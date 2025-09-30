# CBH BCP Python Server Option

This branch preserves the **Python HTTP Server approach** as an alternative to the PHP/Synology Web Station solution.

## Architecture: Python HTTP Server (Alternative)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON SERVER APPROACH                      │
├─────────────────────────────────────────────────────────────────┤
│ VPN Connection → Python HTTP Server → CSV File → Web Interface │
│                                                                 │
│ Components:                                                     │
│ • nas-http-server.py: Custom Python REST API                   │
│ • Direct CSV file access with full control                     │
│ • Custom authentication and logging                            │
│ • Advanced error handling and PHI compliance                   │
└─────────────────────────────────────────────────────────────────┘
```

## Advantages of Python Approach:
- **Full Control**: Complete control over API behavior and security
- **Advanced Features**: Custom authentication, detailed logging, advanced search
- **No Web Station Dependencies**: Bypasses Synology Web Station limitations
- **REST API**: Clean RESTful URLs (/bcp-api/health, /bcp-api/search)
- **Extensible**: Easy to add new features like caching, database integration

## Implementation Status:
- ✅ **nas-http-server.py**: Complete Python implementation
- ✅ **VPN Integration**: Works with existing transfer_to_nas.py automation
- ✅ **PHI Compliance**: Proper security headers and audit logging
- ✅ **CSV Processing**: Handles multi-row patient data format
- 🚧 **Deployment**: Requires custom process management on NAS

## Deployment Options:
1. **Direct Python Execution**: Run python server directly on NAS
2. **Containerized**: Docker container for isolated execution  
3. **Service Integration**: Integrate with Synology Package Center
4. **Hybrid**: Python backend with Nginx proxy

## Why This Wasn't Chosen:
The PHP/Web Station approach was selected because:
- Leverages existing Synology infrastructure
- Simpler deployment and management
- No need for custom process management
- Web Station provides built-in security and monitoring

## Future Considerations:
This Python approach could be revisited if:
- Advanced features are needed (real-time data, complex search)
- Custom authentication requirements emerge
- Performance optimization is required
- Database integration becomes necessary

## Files in This Branch:
- `nas-http-server.py`: Complete Python server implementation
- `README-PYTHON-OPTION.md`: This documentation
- Development and testing utilities

---

**Status**: Complete alternative implementation preserved for future use
**Production Choice**: PHP/Web Station approach (http-web-access branch)