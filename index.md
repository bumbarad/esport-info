## Welcome to Esport-info webpage

The purpose of this webpage is to describe the development of an python-flask application Esport-info, as a part of a CTU subject VIA.
The application purpose is to offer compact information about current e-sport happenings, together with statistics, player information and more. The application will be using https://liquipedia.net/ and https://www.twitch.tv/ API to collect information about players, events and streams.


### 5.11.2020 Base structure

A base structure of the application was added via HTML templates. Also the base design was created using CSS files. For now the focus is aimed at the two biggest CS:GO competition organizers - ESL and Dreamhack.


### 6.11.2020 Embedding Twitch

Important part of the website are embedded online streams using Twitch website. Online streaming was added for ESL and Dreamhack pages. Another significant part of the application will be the Twitch API. For now using this API is a work in progress, however the code was updated to hold the basic API communication structure. Also the API usage was assured at twitch website by registration of the application.


### 22.11.2020 Refactoring Twitch and adding own API

For convenience twitch API functions were refactored into a stand alone class and file. Also an API was created together with interactive swagger ui. Api allows user to gain basic information about any stream from Twitch, making the communication way easier than using official twitch API. Also it is possible to add/delete twitch channels to a watch list, which leads to a creation of a new page for each new channel.


### 23.11.2020 Minor changes

Some refactoring and more systematic approach was done. Limited impact on functionality. Also the code was added to github.

### 1.12.2020 basic API finalized

Basic api functions were implemented and tested. Added forms using the same API.

### 11.12.2020 Adding Liquipedia API, fulfitting formal requirements 

Liquipedia API was added. Trough API requests application obtains and decomposes required data about teams. However it is not possible to guarantee successfull data extraction. Team names, which are later feeded to the Liquipedia GET request are extracted from stream titles. Sometimes title contains a typo, special characters or abbreviation due to excessive name length of some teams (for example Complexity Gaming is ofter refered as Complexity, etc. I have made attemtps to fit some abbreviation, nevertheless it is not possible for each team and abbreviation of name in the stream title is unpredictable).

Formal requirements should be fulfit with this update, however there are ways how to improve the application in case of need.

### Docker: https://hub.docker.com/repository/docker/bumbarad/esport-info



