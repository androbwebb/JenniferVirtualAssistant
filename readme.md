# Jennifer
###### An open source virtual Assistant
> For those wondering why the first commit is so monolithic, it's because I erased the git history after removing a feature due to a cease and disist order.

[![Build Status](https://travis-ci.org/androbwebb/JenniferVirtualAssistant.svg?branch=master)](https://travis-ci.org/androbwebb/JenniferVirtualAssistant)
[![Codacy Badge](https://api.codacy.com/project/badge/coverage/e3604515bed64b77a0638392bd75fdf5)](https://www.codacy.com/app/awebb/JenniferVirtualAssistant)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/e3604515bed64b77a0638392bd75fdf5)](https://www.codacy.com/app/awebb/JenniferVirtualAssistant)

Inspired by [Jasper Client](https://github.com/jasperproject/jasper-client) but built from scratch to be smarter and
more powerful.

## :checkered_flag: Goals & Reasons for building Jennifer
- *MUCH* Less coupling between the brain & the client interface
- Easier plugin interface
- Better security between plugins
- Simpler API
- More efficient brain


## :speech_balloon: Responding Modules:
Active modules that are triggered by input

| Name | Status | Description |
| ---- | ------ | ----------- |
| **Time** | [Here](https://github.com/androbwebb/JenniferVirtualAssistant/tree/master/lessons/JenniferTimePlugin) | Ask Jennifer what the time or date is and she responds.  |
| **Find My iPhone** | [Here](https://github.com/androbwebb/JenniferVirtualAssistant/tree/master/lessons/JenniferFindMyIphonePlugin) | Jennifer can use the apple find my iphone API to make your iPhone ring |
| **GMail** | [Here](https://github.com/androbwebb/JenniferVirtualAssistant/tree/master/lessons/JenniferGmailPlugin) | Jennifer will read new Gmail emails if you ask. |
| **Conversions** | [Here](https://github.com/androbwebb/JenniferVirtualAssistant/tree/master/lessons/JenniferConversionPlugin) | Convert units of measurement |
| **Facebook** | (In dev) | Jennifer will read new Facebook notifications if you ask. | |
| **Yelp** | (Planned) | Jennifer can search yelp for restaurants and answer questions about them |  |
| **Fandango** | (Planned) | Find out when movies are playing near you |



## :ear: Notification Modules
Passive modules that act similar to push notifications

|      Name      |   Status   |         Description        |
| -------------- | ---------- | -------------------------- |
| **GMail** | [Here](https://github.com/androbwebb/JenniferVirtualAssistant/tree/master/lessons/JenniferGmailPlugin) | Jennifer will alert you when you have new gmail notifications. |
| **Facebook** | (In dev) | Jennifer will alert you when you have new facebook notifications. |
| **CouchPotato** | (Planned) | Jennifer will alert you when new movies are downloaded with couch potato. |
| **Alarm** | (Planned) | Jennifer can act as your alarm clock. |
| **Slack** | (Planned) | Read slack messages outloud |
| **Pushover** | (Planned) | A proxy to receive notifications as a [Pushover Open Client](https://pushover.net/api/client) and pass them through to Jennifer |


## :computer: Clients
IO sources, various ways of interacting with Jennifer

| Client | Status | Description |
| ------ | ------ | ----------- |
| **Terminal** | Done | Interact with Jennifer via a text-based command line prompt |
| **iPhone**  | (Planned) | Interact with Jennifer via STT in an iPhone app. |
| **Google STT**  | (Planned) | Interact with Jennifer via any device you can install Google STT on (rPi, Mac OSX) |

## :mailbox_with_mail: Major Todos:
- [ ] Respect quiet hours for notifications
- [ ] Bite the bullet and make an actual client with STT
- [ ] Make a music-based plugin
- [ ] Use a response type other than JenniferReponseTextSegment

## :cool: Smaller Todos:
- [ ] Make a news plugin (or something that is actually interesting)
- [ ] Make an alarm clock
- [ ] Think about how this would play into hardware (Tie a button to alarm clock?)
- [ ] Control Plex?

# :page_facing_up: License
```
The MIT License (MIT)

Copyright (c) 2016 Andrew Webb

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

SOUNDS: The sound files in `/ioclients/assets/` are under [Creative Commons 3 License](http://creativecommons.org/licenses/by/3.0/us/) thanks to [dev_tones](http://rcptones.com/dev_tones/)

# :ledger: API Guide

## Overview
Jennifer is a `brain` and `clients`. The `brain` does processing of input and returns output. `client`s are
responsible for all IO. A client can be any type and combination of input and output. Imagine Amazon's Alexa: it has
microphone input and speaker output. I didn't want to lock Jennifer to only audible IO however. Included in this package
is a terminal-based client for pure text input and output. You could also connect a raspberry PI to a screen, and show
only output in visual formats.

### Lessons (Plugins)
A `lesson` is a set of related functionality that extends the capability of the `brain` to complete some tasks.
For example, `JenniferGmailPlugin` brings 3 functions:

1. Count the number of unread emails in GMail account
2. Read my unread emails outloud
3. Notify me when I have new emails



      Type    |             Class            |  Description  |
|:------------:|:----------------------------:| ------------- |
|    Response  |   `JenniferResponsePlugin`   | A plugin that responds when triggered by a set of commands: examples: `JenniferTimePlugin`, `JenniferFindMyIphonePlugin`)
| Notification | `JenniferNotificationPlugin` | A wrapper for a background task. Upon initiation, creates a task that runs on an interval or at a specified time. Examples: `JenniferGmailNotificationPlugin`

#### ResponsePlugin
All response plugins must implement at least three things:

- `VERBOSE_NAME` property must be set with a short description of what it does. For example, `JenniferTimePlugin` would have `VERBOSE_NAME = 'Tell the time or date'`
- `can_respond(**kwargs)` must return a boolean indicating if the plugin wants control. kwarg specifics below
- `respond(**kwargs)` should run the commands. kwarg specifics below. You can call `client.give_output` (or the shortcut `client.give_output_string`) for output, but don't `return` unless you are ready for the plugin to give up control.

| kwarg | Info |
| --- | --- |
| `tags` | a set of [NLTK](https://github.com/nltk/nltk) parsed tags. Each word is matches with it's best guess part of speech.|
| `plain_text` | the plain text that was given from the client |
| `client`|- the client currently running. |
| `brain` | the brain. likely won't be used.. might be deprecated later. |


todo

### Clients
Types of clients
