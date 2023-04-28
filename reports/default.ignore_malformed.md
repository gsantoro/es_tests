|                  | integer   | date   | date_nanos   | ip   | ip_range   | date_range   | object   |
|------------------|-----------|--------|--------------|------|------------|--------------|----------|
| type: integer    | ◻         | 🌤️     | 🌤️           | 🌤️   | 🌤️         | ⛈️           | ⛈️       |
| type: date       | ☀️        | ◻      | ☀️           | 🌤️   | 🌤️         | ⛈️           | ⛈️       |
| type: date_nanos | 🌤️        | ☀️     | ◻            | 🌤️   | 🌤️         | ⛈️           | ⛈️       |
| type: ip         | 🌤️        | 🌤️     | 🌤️           | ◻    | 🌤️         | ⛈️           | ⛈️       |
| type: ip_range   | ⛈️        | ⛈️     | ⛈️           | ☁️   | ◻          | ⛈️           | ⛈️       |
| type: date_range | ⛈️        | ⛈️     | ⛈️           | ⛈️   | ⛈️         | ◻            | ⛈️       |
| type: object     | ⛈️        | ⛈️     | ⛈️           | ⛈️   | ⛈️         | ☀️           | ◻        |

Legend:
- skipped: ◻
- passed: ☀️
- ignored: 🌤️
- failed: ⛈️
- partially_failed: ☁️