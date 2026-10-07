# ALI Studio Pro 4.2.0 — Windows Final Build Guide

## 1. Required host tools

Use a Windows 10/11 x64 build host with:

- Node.js 22.x + npm
- .NET 8 SDK
- Python 3.11.9 only for preparing the embedded runtime, not for end users
- Git
- Visual Studio Build Tools / native toolchain needed by node-pty and PyTorch wheels

## 2. Prepare Electron
