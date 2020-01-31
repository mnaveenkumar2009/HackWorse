# HackWorse
### _**Atom.pdf explains features of the project. Last slide of Atom.pdf has the YouTube demonstration link, devfolio submission link, etc.**_

Steps to test Atom.

1. Create a bot on Zulip. https://zulipchat.com/help/add-a-bot-or-integration
 
2. Clone the project ```git clone https://github.com/mnaveenkumar2009/HackWorse```

3. Download the ```zuliprc``` for the created bot. Place this file inside HackWorse folder.
4. Go to HackWorse folder ```cd HackWorse```
5. Run ```pip3 install zulip_bots wikipedia sympy google``` to install the required libraries.
6. To run the bot use command ```zulip-run-bot atom.py --config-file zuliprc```


