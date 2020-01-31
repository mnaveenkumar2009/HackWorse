# HackWorse
### _**Atom.pdf explains features of the project. Last slide of Atom.pdf has the YouTube demonstration link, devfolio submission link, etc.**_

Steps to test Atom.

1. Create a bot on Zulip. https://zulipchat.com/help/add-a-bot-or-integration
 
2. Clone the project ```git clone https://github.com/mnaveenkumar2009/HackWorse```

3. Download the ```zuliprc``` for the created bot. Place this file inside HackWorse folder.
4. Go to HackWorse folder ```cd HackWorse```
5. Run ```pip3 install zulip_bots wikipedia sympy google BeautifulSoup4``` to install the required libraries.
6. To run the bot use command ```zulip-run-bot atom.py --config-file zuliprc```

### Commands 
Atom can follow these commands:
1. ```prodcuts``` will give the balanced chemical equations along with steps. Example ```products CH4 + O2```
2. Unbalanced equations can be added using ```add``` command. The algorithm will use these basic equations to solve complex ones. Example ```add C10H20 + O2 = CO2 + H2O 1072```, here 1072 is the enthalpy of the equation.
3. ```explain_product``` will give properties of any chemical compund. Example ```explain_product NaOH NaCl```
4. ```structure``` command gives the structure of the chemical compund. Example ```structure oxalic acid```
5. Any generic doubts can be solved by simply entering the query. Example ```What is acid based reaction```, ```Define acid base reaction```, etc. 


