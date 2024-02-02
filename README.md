# Outpost CLI

This is a Outpost CLI for [Outpost](https://outpost.run). It lets you run models from your terminal, and do various other things on Outpost.

## Requirements

- Python 3.8+

## Getting Started

Install the library with
```
pip install outpostcli

outpostcli login [-t api_token]
```

## Get Current User
```
outpostcli user [-t api_token]
```

## List Inferences
```
outpostcli inferences list [-e entity] [-t api_token]
```

## Get Inference
```
outpostcli inference get <inf_name> [-e entity] [-t api_token] 
#TODO: outpostcli inference <inf_name> get ...
```

## Examples
```
outpostcli user
outpostcli inferences create hf:lxyuan/distilbert-base-multilingual-cased-sentiments-student -i CPU-sm -n cli-text-classification 
```