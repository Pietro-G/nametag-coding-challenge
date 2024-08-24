# nametag-coding-challenge
Write a program that updates itself. Imagine that you have a program you’ve deployed to clients and you will periodically produce new versions. When a new version is produced, we want the deployed programs to be seamlessly replaced by a new version.

Please write what you consider to be production quality code, whatever that means to you. You may choose any common programming language you like (Go, Rust, or C++ would be good choices). Your program should reasonably be expected to work across common desktop operating systems (Windows, Mac, Linux). If your scheme requires non-trivial server components, please write those as well.

As in real life, answers to clarifying questions may be elusive. If you have a question, write it down, and guess what you think our answer might be, and proceed as if that were the answer.

# Populating the .env:
1. Add Github Username / Repo in .env
2. To generate a token go to: Settings > Developer Settings > Select Personal Access Tokens > Generate New Token

# Running the server:
`make run-server`

# Running the client:
`make run-client`

# Creating a new version:
Whenever a tag is pushed with udpates, the cicd in this project will create cross-platform compatible updates. The server is configured to specifically looked for tagged released in order to check for updates, therefore the underlying assumption is that a tagged version of the software exists.

# Running an update:
If there is an update available, `make update` should fetch the latest executable, if the latest update isn't running, the executable will halt and ask the user to updates.