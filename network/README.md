### Server software for GSF Parser

This directory contains the files `strategy_clienthandler.py` and `strategy_server.py` to allow communication with 
`Client` instances from `tools.strategy_client.Client` for real-time editing and sharing of Strategy objects and Phases.

Running a `Server` requires admin privileges on the system, and is not advised if untrusted `Client`s are expected. 
Remote code execution should not be possible, but the security of the systems is not guaranteed.

All communication between `Server`, `ClientHandler` and `Client` is unencrypted. The moment a `Client` connects to your
`Server`, the master `Client` will send all Strategies and there is currently no option to prevent this. Treat this 
functionality with caution for the time being if you have secret Strategies or have included privileged information
in one or more `Strategy` objects.

As found in `README.md` in the root of this project, the warranty disclaimer:
```
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
```
