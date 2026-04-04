# IBKR Flex Query XML Downloader

Small Python utility for downloading an Interactive Brokers Flex Query statement as XML.

The script performs the full Flex Web Service flow:

1. Request statement generation from IBKR
2. Poll until the statement is ready
3. Save the XML response to disk

The repository is intentionally lightweight:

- single Python script
- standard library only
- no third-party dependencies
- no package/build system

## Features

- Downloads IBKR Flex Query XML using a token and report number
- Retries while the statement is still being generated
- Saves the final XML to a local file
- Can be used from the terminal or imported from Python code
- Uses only Python standard library modules

## Repository Contents

- `IBKR_xml_downloader.py`: main script and importable function
- `README.md`: project documentation

## Requirements

- Python 3
- A valid Interactive Brokers Flex Web Service token
- A valid Flex Query report number configured in your IBKR account
- Network access to IBKR Flex Web Service endpoints

Check your Python version:

```bash
python --version
```

## Installation

No pip installation is required for this project because it has no external dependencies.

Clone or copy the repository and run the script directly.

If you want an isolated environment anyway:

```bash
python -m venv .venv
source .venv/bin/activate
```

There is currently no `requirements.txt` because the script only uses the standard library.

## How It Works

The script talks to the Interactive Brokers Flex Statement service in two phases.

### Phase 1: Submit request

It sends your:

- token
- report number
- request version

to the IBKR request endpoint.

If IBKR accepts the request, the service returns:

- a polling URL
- a reference code

### Phase 2: Poll for completion

The script waits, then polls the returned URL until one of the following happens:

- the statement is ready and XML is returned
- IBKR responds that generation is still in progress
- IBKR returns an error
- retries are exhausted

### Phase 3: Save XML

Once the XML statement is available, it is written directly to the output file.

## Command Line Usage

The script can be run directly from the terminal.

### Syntax

```bash
python IBKR_xml_downloader.py TOKEN REPORT_NUMBER [FILENAME]
```

### Positional Arguments

- `TOKEN`: IBKR Flex Web Service token
- `REPORT_NUMBER`: IBKR Flex Query report number
- `FILENAME`: optional output file name

### Default Output File

If `FILENAME` is omitted, the script writes to:

```text
statement.xml
```

### Examples

Use the default output file:

```bash
python IBKR_xml_downloader.py YOUR_TOKEN YOUR_REPORT_NUMBER
```

Write to a custom file:

```bash
python IBKR_xml_downloader.py YOUR_TOKEN YOUR_REPORT_NUMBER my_statement.xml
```

If the file has execute permission, you can also run it directly:

```bash
./IBKR_xml_downloader.py YOUR_TOKEN YOUR_REPORT_NUMBER
```

## Python Usage

The script also exposes a function you can import:

```python
from IBKR_xml_downloader import download_xml

download_xml("YOUR_TOKEN", "YOUR_REPORT_NUMBER")
download_xml("YOUR_TOKEN", "YOUR_REPORT_NUMBER", "my_statement.xml")
```

Function signature:

```python
download_xml(token, report_number, filename='statement.xml')
```

## Output

On success, the script writes the downloaded XML statement to the selected file.

Typical console output looks like this:

```text
Downloading FlexQuery XML-Data...
XML request is Success
Waiting 5 seconds before fetching XML
XML is not yet ready.
Waiting 15 seconds before fetching XML
XML download is successful.
Flexquery XML Download completed!
```

## Retry Behavior

The script currently uses these built-in retry settings:

- initial wait: `5` seconds
- retry count: `7`
- wait increment: `10` seconds per retry

That means the polling waits are:

- 5 seconds
- 15 seconds
- 25 seconds
- 35 seconds
- 45 seconds
- 55 seconds
- 65 seconds

These values are currently hard-coded in `IBKR_xml_downloader.py`.

## Error Handling

The script currently exits with status code `1` when it encounters an unrecoverable error.

Examples of failure cases:

- IBKR rejects the initial request
- IBKR returns an unexpected response missing download details
- polling returns an IBKR error code other than `1019`
- all retries are exhausted before the XML is ready

Current behavior is intentionally simple and CLI-oriented.

## Security Notes

- Do not commit your IBKR token to source control
- Avoid pasting real credentials into shell history on shared systems
- Be careful when logging command lines in CI or shared terminals
- The script writes to whatever filename you provide, so use a trusted output path

## Limitations

- No automated tests are included
- No timeout handling is implemented for HTTP requests
- No packaging metadata is included
- No structured logging is included
- No async or concurrent downloads are implemented
- No validation is performed beyond basic XML field checks

## Validation

There is no formal test suite in this repository.

The main validation command is:

```bash
python -m py_compile IBKR_xml_downloader.py
```

## Development Notes

- The repository currently contains a single Python module
- The script uses only standard library imports
- The main public entrypoint is `download_xml(...)`
- The CLI is implemented with `argparse`

## Troubleshooting

### The request is rejected

Possible causes:

- invalid token
- invalid report number
- IBKR service-side issue

Verify your token and report configuration in Interactive Brokers.

### The XML never becomes ready

Possible causes:

- IBKR is slow generating the report
- temporary IBKR service issue
- request parameters are valid but the backend is delayed

Try again later or increase retry behavior in the script.

### The script exits immediately with an error

Possible causes:

- IBKR returned an error code
- response XML structure was not what the script expected
- local file path could not be written

Review the printed console output for the reported error code or message.

## Example Workflow

1. Create a Flex Query report in your IBKR account
2. Obtain your Flex Web Service token
3. Run the script with your token and report number
4. Open the saved XML file in your downstream workflow or parser

## Future Improvements

Possible enhancements if you want to extend the project:

- add request timeouts
- add automated tests with mocked IBKR responses
- support downloading multiple reports
- expose retry settings via CLI flags
- return structured exceptions for library use
- add optional JSON or CSV conversion steps

## License

This project is published under the MIT License.

If you have not already done so, add a `LICENSE` file containing the standard MIT license text.
