# ChatboxPi
---
- 2nd Round, 2019 AIoT Hackathon
- team member : Shu-Hsiang Yang, Sheng-Je Huang, Yu-Min Huang, Yi-Hsiang Chen
---
This is a Chinese voice assistance written on Raspberry pi.

The overall flow chart illustrated below.
+ flow chart  
<img src="figures/architecture.png" width="80%" height="30%" />
The input voice is received by the microphone.
After the activation/trigger of the microphone.
The audio is recorded.
And then we use API from Chunghwa Telecom to transform the speech to text.
Given the input text, our dialogue system will act or reply.
The details in our dialogue system will be described in following section.
Next, we use another Chunghwa Telecom API transform the response to voice.
Finally, the voice will output form the speaker.

---
+ The appearance of 
<img src="figures/appearance.png" width="30%" height="80%" />
---
