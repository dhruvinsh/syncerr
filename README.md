# Syncerr ♻️

Syncerr is a Python-based utility that synchronizes watch status and media metadata
between Jellyfin and Plex media servers. It enables seamless tracking of your viewing
progress across platforms, ensuring consistent watch history no matter which server
you're using.

## Features

- **Bi-directional Synchronization**: Sync watch status from Jellyfin to Plex
  and vice versa
- **Currently Playing Sync**: Real-time synchronization of actively playing content
- **Watch History Sync**: Synchronize previously watched content between platforms
- **Multi-user Support**: Works with multiple user accounts across both platforms
- **Type-Safe Implementation**: Fully typed Python codebase with comprehensive schema
  validation
- **Modern Python**: Built with Python 3.12+ features and best practices

## Installation

### Prerequisites

- Python 3.12 or higher
- Jellyfin server with API access
- Plex server with API token

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/syncerr.git
   cd syncerr
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   ```

3. Create a configuration file:

   ```bash
   cp config.yaml.example config.yaml
   ```

4. Update the configuration with your Jellyfin and Plex credentials:

   ```yaml
   # config.yaml
   LOG_LEVEL: INFO

   # Plex config
   PLEX_URL: https://your-plex-server:32400
   PLEX_TOKEN: your-plex-token

   # Jellyfin config
   JELLYFIN_URL: https://your-jellyfin-server:8096
   JELLYFIN_USERNAME: your-jellyfin-username
   JELLYFIN_PASSWORD: your-jellyfin-password
   ```

## Usage

Run the synchronization tool:

```bash
python run.py
```

For scheduled synchronization, you can set up a cron job or systemd timer.

## Architecture

Syncerr follows a clean, modular architecture:

- **API Layer**: Interfaces for Jellyfin and Plex servers
- **Schema Layer**: Pydantic models for media types and metadata
- **Engine**: HTTP client for API communication
- **Configuration**: Environment-based configuration management

## Configuration Options

| Option            | Description                                     | Default    |
| ----------------- | ----------------------------------------------- | ---------- |
| LOG_LEVEL         | Logging verbosity (ERROR, WARNING, INFO, DEBUG) | INFO       |
| PLEX_URL          | URL of your Plex server                         | (Required) |
| PLEX_TOKEN        | Authentication token for Plex                   | (Required) |
| JELLYFIN_URL      | URL of your Jellyfin server                     | (Required) |
| JELLYFIN_USERNAME | Jellyfin username                               | (Required) |
| JELLYFIN_PASSWORD | Jellyfin password                               | (Required) |

## Roadmap 🛣️

Below are plan list and they are in order:

- [x] Jellyfin currently playing media sync to Plex
- [x] Multi-user support for Jellyfin to Plex
- [ ] Synchronous API for Jellyfin and Plex
- [ ] Implement proper run Job
- [ ] Jellyfin already played media sync to Plex
- [ ] Plex currently playing media sync to Plex
- [ ] Plex already played media sync to Jellyfin
- [ ] Library names regex support

## Dependencies

- [httpx](https://www.python-httpx.org/): Modern HTTP client with sync and
  async APIs
- [pydantic](https://docs.pydantic.dev/): Data validation and parsing
- [loguru](https://github.com/Delgan/loguru): Python logging made simple
- [omegaconf](https://omegaconf.readthedocs.io/): Flexible configuration system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Help Required

I am looking for nice logo, any help is appreciated. Feel free to create a pull
request if you feel like doing it.

## License

This project is licensed under the GPL3 License - see the LICENSE file for details.
