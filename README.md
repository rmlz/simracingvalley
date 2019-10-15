<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo, twitter_handle, email
-->





<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/rmlz/simracingvalley">
  </a>

  <h3 align="center">Simracing Valley</h3>

  <p align="center">
    Source code for a player aggregator system for the <a href="http://www.game-automobilista.com/br/">REIZA'S GAME-AUTOMOBILISTA</a>.
    <br />
    <br />
    <a href="https://github.com/rmlz/simracingvalley/issues">Report Bug</a>
    ·
    <a href="https://github.com/rmlz/simracingvalley/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Features](#built-with)
  * [Built With](#built-with)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)




<!-- ABOUT THE PROJECT -->
## About The Project

[![Simracing Valley]](https://github.com/rmlz/simracingvalley)

This is the source code of a very personal project that I worked in the 2017-2018 years. Now anyone can create your own "Player aggregator" for the Reiza's [Game-Automobilista](http://www.game-automobilista.com/br/) simulator.

This code is totally prepared to be uploaded on [AMAZON-AWS](https://aws.amazon.com/pt/)! All you need to do is to ZIP it and upload it into your own server!

I'll not teach how to edit the code. It's important that you know some python, and that you have the will to learn and create your own system. It's also known that you know some mongodb, or at least how to translate the mongodb queries to a SQL format inside the code and implement your own SQL database.

If you have any doubt about the code, I may help you as I'm not creating a full documentation. Just open an [issue](https://github.com/rmlz/simracingvalley/issues)!

Servercontrol.py contains the "automation bot" that will start servers, save race data to database and finish it. **This way you can save an entire agenda of automated servers that will start and end after saving racing results!** It's just **AWESOME!!**

### Features
* Player account and personal profile;
* Accounts are STEAM-linked;
* Ranking;
* Races logs and records;
* Driver's evolution through season;
* Dedicated server menagement from website;
* Safe storage of personal data (encryption!);



### Built With

* [Python-Flask](https://www.fullstackpython.com/flask.html)
* [AMAZON-AWS](https://aws.amazon.com/pt/)
* [MONGO-DB](https://www.mongodb.com/)
* [Sublee's Trueskill](https://github.com/sublee/trueskill)


<!-- GETTING STARTED -->

### Prerequisites

Development skills and the will of learning Python-Flask

### Installation
 
1. Create an Amazon-AWS account.
2. Open a new server.
3. Download or clone this git to your computer
```sh
git clone https:://github.com/your_username_/Project-Name.git
```
4. Move the servercontrol.py file to your Dedicated Server folder 
5. Zip the cloned folder and upload it to AWS.
6. Access your new website.

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. There are lots that can be implemented to such a simple code and lots that can be refactored. Any contribution is **greatly appreciated**!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Ramon Pinto de Barros
[Email](mailto:pbarrosramon@gmail.com)

## Acknowledgements

**Why am I opening the source code?** Well, I have no time to manage such a site like this! By opening the code I make my contribution available
to everyone which wants to study or implement the code inside their own projects!

I'm a Python student that have been trying to create useful scripts for the Simracing Community. 
Also I may thanks all the people that helped me to develop the Simracing Valley Community:

* Alisson Zanoni
* Aparicio Felix Neto
* Aurea Barros
* Carlos Eduardo Pinto
* Celso Pedri
* Cesar Louro
* Fabio Krek
* Fernando Bueno
* Glenio Lobo
* Gracas Barros
* Gustavo Pinto
* Hernani Klehm
* Iovan Lima
* Maikon Sulivan
* Matheus Manarim
* Nicolas Sanchez Ernest
* Pedro Phelipe Porto
* Rodrigo Lepri
* Rodrigo Vicente
* Tadeu Costa
* Tayane Campos


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/rmlz/simracingvalley.svg?style=flat-square
[contributors-url]: https://github.com/rmlz/simracingvalley/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/rmlz/simracingvalley.svg?style=flat-square
[forks-url]: https://github.com/rmlz/simracingvalley/network/members
[stars-shield]: https://img.shields.io/github/stars/rmlz/simracingvalley.svg?style=flat-square
[stars-url]: https://github.com/rmlz/simracingvalley/stargazers
[issues-shield]: https://img.shields.io/github/issues/rmlz/simracingvalley.svg?style=flat-square
[issues-url]: https://github.com/rmlz/simracingvalley/issues
[license-shield]: https://img.shields.io/github/license/rmlz/simracingvalley.svg?style=flat-square
[license-url]: https://github.com/rmlz/simracingvalley/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/ramon-pinto-de-barros-a4527a72/

