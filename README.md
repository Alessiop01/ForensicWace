# Forensic Wace

Welcome to the repository of Forensic Wace, my Bachelor's thesis project in Computer Forensics. This project represents the result of my study focused on the extraction of chats and other informations contained inside the whatsapp database, extracted from Apple iOS devices.

```
    ______                           _         _       __              
   / ____/___  ________  ____  _____(_)____   | |     / /___ _________ 
  / /_  / __ \/ ___/ _ \/ __ \/ ___/ / ___/   | | /| / / __ `/ ___/ _ \
 / __/ / /_/ / /  /  __/ / / (__  ) / /__     | |/ |/ / /_/ / /__/  __/
/_/    \____/_/   \___/_/ /_/____/_/\___/     |__/|__/\__,_/\___/\___/ 
```

## Prerequisites
In order to use the "Available Backups" function, [Apple iTunes](https://www.apple.com/it/itunes/download/index.html) must be installed on the computer and at least one backup of any device must have been made.

If this is not the case, the function will not work and will show the user the following error message.

```
Internal Server Error

The server encountered an internal error and was unable to complete your request.
Either the server is overloaded or there is an error in the application.
```

In addition, if you think you also need to work with and manage encrypted and password-protected backups, an additional package will need to be installed.

All you have to do is run the following script in a command prompt window.

```bash
pip install git+https://github.com/KnugiHK/iphone_backup_decrypt
```

## Installation

In order to start using the Forensic Wace you need to install it.

To do this, open a terminal window as administrator and run the command below.

```bash
pip install git+https://github.com/Alessiop01/ForensicWace.git
```

## Usage
To start the Forensic Wace GUI, execute the command below in any terminal window:

```python
forensic-wace
```

## Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)