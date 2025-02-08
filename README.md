# Django Boilerplate todolist

**THIS README NEEDS COMPLETING**

This repository contains [...] which does [...] in order to [...].

## Documentation

The project has detailed documentation for developers, including a "getting
started" guide. See below for information on building the documentation.

## Guidebook - Quickstart and Testing

To know how to get started with this project visit our [Guidebook](https://guidebook.devops.uis.cam.ac.uk/en/latest/notes/webapp-dev-environment/).

To view notes on how to get the project working locally visit the [getting started section](https://guidebook.devops.uis.cam.ac.uk/en/latest/notes/webapp-dev-environment/#getting-started-with-a-project) of the Guidebook.

To get started with Testing visit our [testing section](https://guidebook.devops.uis.cam.ac.uk/en/latest/notes/webapp-dev-environment/#running-tests) of the Guidebook.

## Loading secrets at runtime

If the `EXTRA_SETTINGS_URLS` environment variable is non-empty it is interpreted
as a comma-separated set of URLs from which to fetch settings. Settings are
fetched and applied in the order they are listed.

The settings should be in the form of a YAML document which is fetched, parsed
and interpolated into the Django settings when the server starts.

`EXTRA_SETTINGS_URLS` currently understands the following URL schemes:

* file://... URLs are loaded from the local file system. If the URL
  lacks any scheme, it is assumed to be a file URL.
* https://... URLs are fetched using HTTP over TLS.
* gs://BUCKET/LOCATION formatted URLs specify a Google Cloud Storage
  bucket and a location within that bucket of an object to load settings
  from.
* sm://PROJECT/SECRET#VERSION formatted URLs specify a Google Secret
  Manager secret to load settings from. If the version is omitted, the
  latest version is used.

For Google Cloud Storage and Secret Manager URLs, application default
credentials are used to authenticate to Google.

Settings which can be loaded from external YAML documents can also be specified
in environment variables. A variable of the form EXTERNAL_SETTING_[NAME] is
imported as the setting "NAME" and the value of the variable is interpreted as a
YAML formatted value for the setting.

## Notes on debugging

The Full-screen console debugger `pudb` has been included to allow you to run a debug in the
docker-compose environment. To use, simply set the breakpoint using `import pdb; pdb.set_trace()`
and attach to the container using:

```bash
docker attach todolist_development_app_1
```

For a fuller description of how to debug follow the
[guide to debugging with pdb and Docker](https://blog.lucasferreira.org/howto/2017/06/03/running-pdb-with-docker-and-gunicorn.html)
(it works just as well for `pudb`).

## CI configuration

The project is configured with Gitlab AutoDevOps via Gitlab CI using the .gitlab-ci.yml file.

## Copyright License

See the [LICENSE](LICENSE) file for details.
