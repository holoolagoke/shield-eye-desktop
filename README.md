# Shield Eye Log Analyzer

- [Shield Eye Log Analyzer](#shield-eye-log-analyzer)
  - [Project Overview](#project-overview)
  - [Features](#features)
    - [Platform Capabilities](#platform-capabilities)
  - [Desktop Installation](#desktop-installation)
    - [Quick Install (Debian/Ubuntu)](#quick-install-debianubuntu)
  - [Getting Started](#getting-started)
    - [Log Event Structure](#log-event-structure)
    - [Application Metadata](#application-metadata)
    - [Network Request Context](#network-request-context)
    - [Creating Log Events](#creating-log-events)
    - [Error Logging Middleware](#error-logging-middleware)
    - [Example Usage](#example-usage)
    - [Database Connection](#database-connection)
    - [Setting Up Preferences](#setting-up-preferences)
  - [Analysis \& Usage](#analysis--usage)
  - [Architecture Philosophy](#architecture-philosophy)
  - [Open Source \& Customization](#open-source--customization)
  - [Contributing](#contributing)
  - [License](#license)
  - [Notes](#notes)
  - [Security Notice](#security-notice)
  - [Acknowledgements](#acknowledgements)
  - [Author](#author)

Shield Eye Log Analyzer is a **manual log event collection and analysis system** designed for developers, SOC analysts, and cybersecurity professionals.  
The system allows developers to define and record meaningful application events, store them in MongoDB, and analyze them using the Shield Eye platform to detect potential security incidents.

This README serves as a **technical manual** for integrating and using the Shield Eye event logger.

## Project Overview

Shield Eye Log Analyzer enables developers to manually create structured log events within their applications.

These events are:

- Stored in the developer’s MongoDB instance
- Read and analyzed by the Shield Eye application
- Used to identify anomalies, security threats, and abnormal behavior

Once a user signs up on Shield Eye, the platform connects to the user’s MongoDB database (read-only) and analyzes the stored logs. **Shield Eye does not store user logs on its own servers.**

## Features

- Manual, developer-controlled log event creation
- Structured logging for security and observability
- Multiple event types (Authentication, System, Network, Application, etc.)
- Configurable severity levels (`info`, `warn`, `error`, `critical`)
- MongoDB-based storage for scalability
- Event tagging for filtering and correlation
- Read-only log analysis through the Shield Eye platform

### Platform Capabilities

[**Web Platform**](https://www.shieldeye.holoolagoke.com)

> ⚠️ **Operational Status**
> The web backend is currently disabled due to infrastructure cost considerations.
>
> The platform will resume operation when:
>
> - At least five active users are registered, or
> - A company requests a technical demonstration or project review.

- Real-time and near-real-time log analysis
- Current-month log scope for performance efficiency
- Lightweight SOC-style monitoring

[**Desktop Platform**](https://github.com/holoolagoke/shield-eye-desktop/tree/master/downloads)  

- Offline log analysis
- Historical log investigation beyond the current month
- JSON log file import from MongoDB exports
- Designed for forensic review and long-term analysis

## Desktop Installation

The Shield Eye Desktop application can be downloaded from:

[Download Shield Eye Desktop (.deb)](https://github.com/holoolagoke/shield-eye-desktop/tree/master/downloads/linux)

Detailed Linux installation instructions are available in the `downloads/INSTALL.md` file within the repository.

### Quick Install (Debian/Ubuntu)

```bash
sudo dpkg -i shieldeye_1.0.0_amd64.deb
sudo apt-get install -f
```

## Getting Started

### Log Event Structure

Each log event follows a consistent structure:

| Field         | Description                                           |
|---------------|-------------------------------------------------------|
| `_id`         | Unique log event identifier                           |
| `timestamp`   | Time the event occurred                               |
| `level`       | Severity level (`info`, `warn`, `error`, `critical`)  |
| `event_type`  | High-level name of the event                          |
| `source`      | File or module where the event originated             |
| `message`     | Human-readable event description                      |
| `stack`       | Error stack trace (if applicable)                     |
| `tags`        | Short keywords for categorization                     |

### Application Metadata

| Field         | Description                       |
|---------------|-----------------------------------|
| `app.name`    | Name of the developer application |
| `app.version` | Application version               |

### Network Request Context

The following fields are automatically captured from the incoming request when available:

```txt
user.id
user.ip
user.method
user.endpoint
user.status
user.user_agent
```

### Creating Log Events

Create a centralized event logger file in your application.

Example Logger Implementation

```js
// shield-eye-logger.js
import { v4 as uuidv4 } from "uuid"
import clientPromise from "..."

// Connect to MongoDB
const client = await clientPromise
const db = client.db("logs")

export async function logEvent(req, res, {
    event_type,
    level = "info",
    category,
    source,
    message,
    stack = "",
    tags = []
}) {
    try {
        const collection = db.collection("event_logs")

        const log = {
            _id: uuidv4(),
            timestamp: new Date(),
            level,
            category,
            event_type,
            source,
            message,
            stack,
            app: {
                name: process.env.APP_NAME || "YourAppName",
                version: process.env.APP_VERSION || "1.0.0"
            },
            user: {
                id: req?.validatedUserId || "anonymous",
                ip: req?.ip || "0.0.0.0",
                method: req?.method || "N/A",
                endpoint: req?.originalUrl || "N/A",
                status: res?.statusCode || null,
                user_agent: req?.headers?.["user-agent"] || "N/A"
            },
            tags
        }

        return await collection.insertOne(log)
    } catch (err) {
        console.error('Error:', err.name)
    }
}
```

### Error Logging Middleware

```js
// shield-eye-logger.js
export function errorEvent(err, req, res, next) {
    logEvent(req, res, {
        event_type: err.name || "UnhandledException",
        category: "Server Error",
        source: req?.originalUrl || "N/A",
        message: err.message,
        stack: err.stack,
        tags: ["error", "exception"]
    })
}
```

### Example Usage

```js
logEvent(req, res, {
    event_type: "Authentication",
    level: "warn",
    category: "auth_failed",
    source: "auth.js",
    message: `${username} login attempt failed due to incorrect password`,
    tags: ["authentication", "login"]
})
```

### Database Connection

Create a database named `logs`

Create a collection named `event_logs`

Shield Eye only scans the database named *logs* and the collection *event_logs*

Database User (Required):

```txt
* Create a MongoDB user named: shield_eye_agent
* Permissions: Read-only
* Restricted to: logs database and event_logs collection
* Add the Shield Eye application IP address to your MongoDB IP allowlist.
```

### Setting Up Preferences

After signing up and logging into your Shield Eye account, configure your preferences.

Required fields:

- **mongoUrl**: mongodb+srv://shield_eye_agent:<strong_password>@...
- **level**: an array of log levels to monitor when creating alerts. Example:

```json
["warn", "error", "critical"]
```

## Analysis & Usage

Logs are collected directly from the user’s MongoDB instance. Shield Eye analyzes logs for anomalies and security patterns

Logs can be filtered by:

- event_type
- level
- category
- tags
- Date
- Word search

Regular review is recommended to detect abnormal behavior early

Best Practices

- Use clear and descriptive message values
- Apply consistent category naming
- Use lowercase tags for consistency
- Avoid logging sensitive data (passwords, tokens, secrets, PII)
- Archive or rotate old logs to prevent database bloat

## Architecture Philosophy

Shield Eye follows a **separation-of-concerns** approach:

- The [**web platform**](https://www.shieldeye.holoolagoke.com) focuses on lightweight, current-month detection and monitoring.
- The [**desktop platform**](https://github.com/holoolagoke/shield-eye-desktop/tree/master/downloads) focuses on deep-dive, offline, and historical forensic analysis.

This design ensures scalability, performance efficiency, and analyst flexibility.

---

## Open Source & Customization

Shield Eye is designed to be extensible.

Interested users may:

- Download the full [source code](https://github.com/holoolagoke/shield-eye-desktop/tree/master/app)
- Customize detection logic
- Implement additional correlation rules
- Modify UI or backend logic for enterprise use
- Extend logging schema to match internal security standards

Developers are encouraged to fork the repository and adapt the platform to meet organizational or research needs.

For upgrade strategies and architectural extension ideas, review the codebase structure and desktop import modules.

## Contributing

The Shield Eye Desktop application provides offline and historical log analysis capabilities.

Future enhancements include:

- Advanced correlation rules
- Timeline-based investigations
- Extended export and reporting features

Contributions, design feedback, and security reviews are welcome.

## License

This project is licensed under the MIT License.

© Holo Olagoke

## Notes

- Logs are not stored on Shield Eye servers. If logs are deleted from your MongoDB instance, they cannot be recovered.
- Only provide MongoDB URLs created with the shield_eye_agent read-only user.
- Shield Eye analyzes logs generated within the current calendar month only (Day 1 – Day 31), at the start of each new month, Shield Eye begins analysis on newly generated logs.
- Investigation of historical logs beyond the current month is not supported in the web version.
- Investigators or developers are encouraged to jot down unusual patterns or export their logs from MongoDB if they want to preserve historical data for offline analysis.
- A desktop version of Shield Eye is available and supports long-term log retention and historical forensic analysis.
- Since logs are stored in the user’s MongoDB instance, they can be exported and uploaded into the Shield Eye Desktop application.
- The desktop version enables investigations beyond the current month without impacting web platform performance.

## Security Notice

- Developers are responsible for ensuring that sensitive information is never logged.
- Shield Eye does not sanitize or redact logs at the source.

## Acknowledgements

This project is supported by continuous learning and professional guidance from the cybersecurity and software engineering community.

Special acknowledgment is given to:

- **[Steven - MyDFIR](https://www.youtube.com/@MyDFIR)**  
For practical SOC-focused training, detection engineering concepts, and real-world defensive security knowledge that influenced Shield Eye’s log analysis and investigation design.

- **[Dave Gray](https://www.youtube.com/@DaveGrayTeachesCode)**  
For foundational and advanced full stack software engineering knowledge that contributed to the architectural design, scalability considerations, and implementation approach of this project.

Their educational content significantly contributed to the skills and knowledge applied in the development of Shield Eye.

## Author

Name: Holo Olagoke Friday  
Career path: Cybersecurity & Software Engineering  
Website: [www.holoolagoke.com](https://www.holoolagoke.com)  
Contact: [contact@holoolagoke.com](mailto:contact@holoolagoke.com)
