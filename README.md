# Batch Cancel CLI

A command-line tool to transfer and then cancel multiple contracts. The way it works is:

1. First it transfers Contract to a new recipient address (that you provide as a first argument to `cancel` command)
2. Then it cancels Contract, with this all unlocked tokens are returned to the New Recipient
3. This way you cancel a Contract/Contracts without sending any tokens to the original recipient

## Run using pre-built binary
- You can use a pre-built binary (with pyinstaller) from `dist` directory like so
  ```./dist/batch_cancel_cli -h```
  This command will show available commands and options for the configuration
- Works the same as with poetry bit without a need to install dependencies
- To launch on windows use `PowerShell`, to launch on Mac OS use `Terminal`

## Run using poetry
- Requires [poetry](https://python-poetry.org/docs/#installation) and python 3.11+ to be installed on your machine
- Install dependencies and a script with
  ```poetry install```
- And run the script with
  ```poetry run batch_cancel_cli -h```
  ```poetry run batch_cancel_cli cancel```

## Example Commands
- This command will transfer 4 Contracts in total to `wdrwhnCv4pzW8beKsbPa4S2UDZrXenjg16KJdKSpb5u` and then cancel them on Mainnet, will use a private key provided via `--key` command lint argument
```
./dist/batch_cancel_cli \
--key yx81aSuUVDEsddhLeyBBv2Qkk2cz5qThj1Ugwk6xPTZUqEnNA3uGGvmChhn3RNdA71jqrvo8nWV9L1Y7pbnSA6v \
cancel \
9k5FjrUEnVBvjmjU7EfxZQCwgTeSirSgFu1ZexaduPCk \
GmW9XSD33jKeM1PWLuBbpZYYkNmdHMz4jkS5FHyVUiGi \
35gRe3qLMHWmUJEYMmEw5wNiKZKmiVAygLLX144evJfZ \
4ojq1wTZ4XWoHjER41uZXpw7cyX68LTE83qiMgC41d9F \
-r wdrwhnCv4pzW8beKsbPa4S2UDZrXenjg16KJdKSpb5u
```

- This command will transfer 4 Contracts in total to `wdrwhnCv4pzW8beKsbPa4S2UDZrXenjg16KJdKSpb5u` and then cancel them on Devnet, will use a custom RPC url and private key located at `signer.json` (default value)
```
./dist/batch_cancel_cli \
--devnet \
--rpc https://rpc.ankr.com/solana_devnet \
cancel \
9k5FjrUEnVBvjmjU7EfxZQCwgTeSirSgFu1ZexaduPCk \
GmW9XSD33jKeM1PWLuBbpZYYkNmdHMz4jkS5FHyVUiGi \
-r wdrwhnCv4pzW8beKsbPa4S2UDZrXenjg16KJdKSpb5u
```
