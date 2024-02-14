# Contributing guide

## Setup Dev
```
git clone https://github.com/outpostHQ/cli

pip install --editable .

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

## Publishing a release

This project has a [GitHub Actions workflow](/.github/workflows/release.yaml) that publishes the `outpostcli` package to PyPI. The release process is triggered by manually creating and pushing a new git tag.

First, set the version number in [pyproject.toml](pyproject.toml) and commit it to the `main` branch:

```
version = "0.0.7"
```

Then run the following in your local checkout:

```sh
git checkout main
git fetch --all --tags
git tag 0.0.7
git push --tags
```

Then visit [github.com/outposthq/outpostkit-python/actions](https://github.com/outposthq/cli/actions) to monitor the release process.