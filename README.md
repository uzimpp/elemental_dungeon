# Incantato 🧙‍♂️

<img width="100%" alt="Screenshot 2568-04-09 at 10 06 45" src="https://github.com/user-attachments/assets/ef749a41-918e-4b93-bdfd-3b6749ad4566" />

## 🎮 What is Incantato?

**Incantato** is a fast-paced survival game where you'll:

* Build a deck of powerful elemental skills
* Fight against waves of challenging enemies
* Master strategic skill combinations

### 🏆 Your Goal
Survive as many waves as possible! Each wave becomes progressively more difficult with stronger and more numerous enemies.

### 🔑 Key Features
* **Deck Building**: Choose 4 unique skills to create your strategy
* **Wave Survival**: Test your skills against endless enemy waves
* **Resource Management**: Balance stamina usage and skill cooldowns
* **Strategic Gameplay**: Experiment with different skill combinations

## 🕹️ Game Features & Controls

| Key | Function |
|-----|----------|
| **WASD** | Move player character |
| **SHIFT** | Sprint (consumes stamina) |
| **SPACE** | Dash (consumes stamina) |
| **1-4** | Use corresponding skill from deck |
| **Mouse** | Aiming or facing direction of player|
| **ESC** | Exit game |

## 🔮 Skills

| Type | Description | How to Use | Tips |
|------------|-------------|------------|----------------|
| **Projectile** | Fast-moving attacks that travel in straight lines and deal damage on impact | Aim with mouse cursor, press corresponding skill key (1-4) to fire | Great for distant targets; aim ahead of moving enemies for better accuracy |
| **Summons** | Creates allies that automatically seek and attack nearby enemies | Press skill key to summon at your location; AI controls the summon afterward | Use to distract enemies while you reposition; effective "tanks" for drawing enemy attention |
| **AOE (Area of Effect)** | Creates expanding damage zones that affect multiple enemies within range | Aim with mouse to target location, press skill key to activate | Most effective against groups of enemies; place strategically to control enemy movement |
| **Slash** | Short-range arc attack that deals high damage directly in front of player | Face direction with mouse, press skill key to execute a quick slash attack | High damage but requires close range; combo with dash for hit-and-run tactics |
| **Chain** | Automatically targets the closest enemy and jumps to nearby targets | Press skill key to activate; automatically finds and chains between targets | Excellent against clustered enemies; no need for precise aiming |
| **Heal** | Restores player health or heals friendly summons | Press skill key to activate healing effect | Save for critical moments; most effective when health is low |

### Skill Management:
* Each skill has a **cooldown period** after use (visible on skill icons)
* Skills can be combined for powerful effects (e.g., summon allies then use AOE to protect them)
* Monitor your **stamina bar** as some skills may require stamina to cast
* Experiment with different skill combinations to find effective strategies

## 👾 Enemies

* **Orc Knight** - Deal more damange, less agile

## 📊 Data

The game records comprehensive data to help you analyze performance:
* Player statistics (waves reached, survival time)
* Skill usage patterns and effectiveness
* Cause of death analysis

## ⚙️ Installation & Setup

1. **Clone Repository:**
   ```bash
   git clone https://github.com/uzimpp/incantato
   cd incantato
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Game

To start the game, make sure your path is in incantato directory

run:
```bash
python src/main.py
```
When the game launches:
1. Enter your name at the prompt
2. You'll see a list of available skills - select 4 to form your deck
3. The game will begin with Wave 1 of enemies
4. Survive as long as possible!

## 🎲 Gameplay Tips

* **Deck Building:** Balance offensive and defensive skills for better survival
* **Stamina Management:** Don't deplete your stamina completely - save some for emergency dashes
* **Positioning:** Use the environment to create bottlenecks for enemies
* **Cooldown Tracking:** Keep an eye on your skill cooldowns to maximize damage output

## 📁 Project Structure

[![](https://mermaid.ink/img/pako:eNrNHGlv2zj2rxj-ssrUMdqZnsGgQJqmbbBtU4zbGeyigMBYtM2NLGlEKonbbX77vvdIWQcPKdPZnc0HWyYfr3cfVL5Ol3nCp0fTZcqkfCnYumTbz9nE_FHr5DXb8snXphX_7hUp2_FycjT5QA-9Xp7x7S5el3lVAMhr_L49xbbbHqBUTPF4yzK2ptlwrQW2vdNNPXBWJSIHsGP87k-1LDnPoLPYrWGW-aIqV2zJe1DLNF9eNkBKwMcJtvXgyirLRLYGyIs8T3ud1-yKx1m1vaA9i0w5kRNniLijiVT9Y-DSMRy9VDFuAGBWac6Ua5VBqGVVljxTsYa-FGkaVxJQB-CJWIahC3ad8SRGagkunUcRmVCCpeILj_WpooM-prjkKsYjWV1FyQtWcncnrU4bsbqWG768jJd5mgop8kzaa1aZvRirpGcp2GK19fSpfL1O4XA4ut35rS8GmtEtQfASOeHEaC-5xVtLGFIy6DuhB4vs6SWQhvPEQ3FZlECnIMiW3SDnbEXGnFQd0ReXfE3iFNhCUjLhAxEy1lBeKSLZd6JumwN3XvGlystGVLdMbea_UuOPPfgNyxKgociKSkWJOnB38yvg_Ig-Z5NtjtxS5HI2Mew_m2T5dX9owuTGZk8mlRa1SAucSG5Gz6jYJY8TtgURjRiMyaztAlavI6m1V4ghSaFa_KindlKWKcVIrvI0ya99hDNQqHLKMEjJElFJH4t4qVsVCXRFWp3MJja91qBPQE9LDmgG9Qc_DfABzKeqIuWOAYmAFbMlj1Ue5WoD6hdooh92B5496nEl8BRoGRyoV8OR5mnnW3I8kZRQNpWATUZx9hVPR8GFSTGgKTacpWrjZJlAF6hnEk8XdoThwaApRrw3ML9wy1jtSTMKBWCkrvhdNQ3LYKtmiZMNK9lS8fK4bnSz_X7MGBkJgdx42nee9sQ3IPGNQEUaoXJKdi5BG9ZFSH9Plz6gERmYnaY5-OslU6uXhkoOg6CFl_xFV5cRiPiClQ4Rb-uwztSW7KPp70v-oTYcKKpvAS-3L5jkC2y57cMVZf4vPH9Knpn2oT_s27ResQaBn7MFh2k_YEG_ncD3xm3k3h_Yx727bAOJ2V2D9jO0BA5rlqEhoVVYkrRNtmXSS45Mo1ESSZ7C0tyMkCAiioVG9AZoeNjVHqd97pH1QJElvOHpFnd3nYjZpDGADv2Gh-OrFWwh0l9edt1P-0edDu2yWvYsX60gChilp-UGtQ7YE55JNI0em0VQSVXW2tkPNBgiaQACjvbrgsYyk3uQZem7okh3ERjug6FjWkjb88H46AEYaguOqrNPM5naFTiU5v0Iz5Z5Dnp5CQf9JwqDXHuNFH1c5NNQ6BnwAGBlsntaGvsqpUpTNydD1ACstHdRozpexV14mF-VYr0GW7If47JBuGItIiBlRrx2wXhvr4Du4mOHfK2gkzbA6uCYiCtkSyL-bKJ5-qZ-2Ll0CCKsr0YDB9bq8__hsBg4KozJyfUMeG1A9Gwl1u5cx5gopY9WzRudkYjFtmUJYPAN-A0W_tCZiLUL5UTi9yCK5m6soMs09A5Yu2tmUEgAjs9P78IMfyZ3NyKKpso6mc268Ln5qzZrsn03-6fdgEHXIsuydcrhxzXnhf4x4qAQo4jsf3VQjA319t25wSVuBqQkW_P_DqoOas_uVyErlp6S_r4dpbM9cXcAUyGLy2-KNMdUZFibNGAhpaldRL6i1Cohv9n2sN_mFnNaOeFRC6qNsz_o7LXV3p-FyjFaecyxv7nKFO3SgbXhtfa1EM6TFa_zBPupXHkE3PRLsDa3cLZZA9oPOCDyLoHHA7NRyjlx07Mo-ZXIK6m3FIvEjUsMahTJlwEj5aKscBUz9F1AO0WuqhIj7bi7dOSaypwtMt9WaJRyVu6BnHl6T4p-dHa-dhY1DiOPVLiidLMaxF2lJwXQThdLnS8m_uvg389-d-C7SrRKX5_O3DUvWN5RdeE3QkX-rISTXb7_1JqzMw89UD1aZLQQ9Y5nlRtRoGZgB6s8awWS-Gv-KrdUDOiXaixoJcUyvqiUImX7gh4CG3wPk4HOK3fuXQ4V98jmeRKRVKGIQ4lPZxJpQekFsBXuHTVJB5g1BXtpiayVnfAALsscAPbBvMN41VNR4sKdMmbbi6rEiMyLch1h5qy9I5Jhx55MnsVgHYtqg1U6ka3diLoAy4NF6SwZyk2HdPOdDtgs6dKkVRFXIngePIh8KSSe330o0ILqEtMaZexhPRtJeLpzY6C-uoul4bOBuSh3AzC_V0INgNxVNFGH4r59e9czNTlN-nn7nYvadQFbAnXAKjec5GZBPxf4y0qZ-ONVM8m1SDwVFwOw4WK9cYtn35GxtVMNsSrxDoJfinV_qHpRz9Sk6SmIcVce9wE7er2AJo9oMVAGtLL0abLaj8n4tX6aTVZ5ueQxXUMI5D2ppqzrtPiwcxYda_QRoqODIS1BOWhDevFFD-glw2yBbnhjiI1Grm0SWsQ3s4nmjtDWrS21IwVrT3ctUukkW52ddDBgIGn4XTmjoSxwyC6ztNiwsEQBfYMr18zvhGhifN_mAn0FTC-WqU8mwKmLfUTCvt1QkOVxnvdBYrDExeTmeAW6UVd8rbJAKdYiwxwVceoQT_81JB63NzCz2o7XaeQRIenepbclfdRlNRNHdyNOsmyfzk51362r0GXGReZ7NqGbeHYQRKpwHLCO6agrcgIYdmrdgkl8c9UV2jTtgjtrUs4ZqEqL48dc9dEzUIRlkBYkmYFx-EUD1xVGXXoANtpgZOyzgNAf4mIXlu9Q3YbZl6lYXkLI3JpCP1KHRxeg3dXbivRXSCdoh8qO7viNOyM0LooL2Q3CaByCuFiHu_MyGZiBWK4TQDjwhBUJRCP0LoE92YU1DWISMRHhx0D5aQ0-jXzBbO2BidkrllZDd0JDMAMYWWFcFgKQm_w6NjR1YALOTleXHNVLbjYW0Wcw-MHo0AQ_7qg3UGQfx1abXF3yXeCemqcWORCyieWns09KpLK_7Z9_xmahds-fuxisd_PAiPFs0mt331op2jdW6iJKvetNAYKOl73gG8A0bYPlH7prbW1_IdBVAQG3DlCvRPGV-14nRV5XeVr5a_UtE9u1e3XJXdzwcr5AMOvWyeomPLleX0E0dyndMZiG4BlKrkfGzQ5DIBT501R29hNY2XTptYD7rMSAygvP8BVLeJxXKqKHrXT2i6yZG8IjAxnWSW3SRPrLk4s1GwucnDAUYYIMVhepLuQ6EaEhNUZdiMAYhzrHbExPNsItQzXgccwC_H1I6UYnT-6Vy61riL-O3Vyuj_aAIOvwW7rCU4QhtB4E9VrrvFkOji3Ex50jf56eG7fc4AOnPCKQz1Mr-aETFhaaoB1v9SlpqYHXx-9O4_fw4Tzyb2cvP75xuuFvTs9ev_no7Hr1YeFsPzl_e_7Lwi3JH94e_-P0l_jF8eI0fvPBOfz4_dm7449n5-_jk_P3r85euyda_P3s7dtF_OGY9m2d6G-T-XwOmjXb6TuNk2WNmWDYpNhJnqb6irvNg2RBvAqWRMdTEgLFBAaAU0oVUzMxv4F4wX6DIkaGysB817NFBwMsGi_llT1Pmq9j_ToL-Cq68qlY1MqRzyb4ioeMS86WG57sK7-YyTXWDFx0nKGO_mAqwGEiXUvReysY1bqXMS_l7BdBY2cezWsNIF6Ucl6V_PeKZ0sqyNPQ_vIA2X0_BkxmlTUlyTjlK1W32YcKmVaPZ-AhO-UGgJarVQTbv_BdmQVnMU_hHLruVmjYoczyr4Jf8_K4KJxVKyS5X3tpugZBNF1XqK4gMGNyjoz_qrQrYXquMZBlnqNbZ1Le84_9l2tQ5YH-v2zBKHU5f2-a-_frKfUlvhDlZfe6gWm9dZm4fcXCHSzpvD5u1Q66gfPkxkzg9ji7mwqWBzo7tUtVrNRl-BoTv4lkzZ2p3h66XJjXiestU0Waq1RczKEBVM38FX31mfamC8tuuJwfw4f1Lk12xWQXFqMskHFZP8Tqkq3XZp0TGvDx8ni9dsfGhudqvZOshm44MF3pkx1c9gE_5oV-ASwMRoGI_IQv4AXhfoO9vQFWy_GFy6GFsQQ4sDsISXBKuVgyBTTsAWtweo_z8_TB5-kkPzw0T-3XN50A7jcyW6A_EOj9-fwH-KHfSTrSqlMGpm29wUn9h4fPja_Ra-yYyl4f6dH6eOb9vMPDfz_v3Do17f0NNO_leQDaL-cZkPn8uasadDSpJN_vQ6PA2oZuHjkDXbihKT6Qm6eLBp1emqmuJunRrV48hnOdDZNxTtd-WVqvR-8p5G0yNheWUTCR7tIHal25gjCDSrYyBkUeD4zu3DC608hO0cIz0hCvuchLKO0lDMy1V1cX3ed0deDVSOdcdA_R1aMv7rl6-ptsU7_NQB1UWb36s6Gbhz1auEAIP_E6uEFQN6Xah0MoN1U8R_QPiMENM1faHIcPj9MXzNpKr3MrrCPmmpWaqzs9brcGE87axXON25ZEeYf1S9d3G0l-UanifGUdjGCaSkOb2l2Y_jwN2zRXcoivehfWevdhXCCOSyousM7lDBeAfdvBBWUma9MBz_eirui32L0P046Dg4DH5j8NQCigyryxMn0yehZ2gfnWdsHay7cO3sYicWT9vxi0B6SVoL7sJR1DkPdrO00eHxgJGV8LtfHM_1K_yT5udhrQCW-PJhC5yVjl7UM4OKa1VC3Oq7w0N3_aY20uIQXVjWdgVVZlEHLuSeewh32bb13ccIwhcaMArk3EXiGU2Na-gdvRWg4VraEaYe5YvKY01VNThv9ozV6Nq11FcPV3MuwugGZRjzvimIdkouVBJLpdxiJb5XvV002ThwTEhnSiTcuM1U3RqeZaiMzw3xGYadvL2aP2Cbmavm2W9iziA20jg2ShvgOuWMuB7TGww9up47wGpY11dEYxbT7shA6ecMYL74trvAP8AU5oT3ak44cOhTz-c3RxbNOR8mZEzOlsCgHAlolkejSlyPrzVG1AFj5Pj-AxYeUlpku_ARyrVL7YZcvpkSorPpuWebXe1D-02jT_W6duLFj2zzzf_1yXuIoZTKr1BPNK06Onjwl2evR1ejM9evRg_tOTh8-ePXv66Nnj-0-ePZhNd9Ojnx48nD999vD-w8cPnjx48PjJo2-z6Rea_P786ZNH9-Hvxx_vP3728PGTh9_-A9OgOOw?type=png)](https://mermaid.live/edit#pako:eNrNHGlv2zj2rxj-ssrUMdqZnsGgQJqmbbBtU4zbGeyigMBYtM2NLGlEKonbbX77vvdIWQcPKdPZnc0HWyYfr3cfVL5Ol3nCp0fTZcqkfCnYumTbz9nE_FHr5DXb8snXphX_7hUp2_FycjT5QA-9Xp7x7S5el3lVAMhr_L49xbbbHqBUTPF4yzK2ptlwrQW2vdNNPXBWJSIHsGP87k-1LDnPoLPYrWGW-aIqV2zJe1DLNF9eNkBKwMcJtvXgyirLRLYGyIs8T3ud1-yKx1m1vaA9i0w5kRNniLijiVT9Y-DSMRy9VDFuAGBWac6Ua5VBqGVVljxTsYa-FGkaVxJQB-CJWIahC3ad8SRGagkunUcRmVCCpeILj_WpooM-prjkKsYjWV1FyQtWcncnrU4bsbqWG768jJd5mgop8kzaa1aZvRirpGcp2GK19fSpfL1O4XA4ut35rS8GmtEtQfASOeHEaC-5xVtLGFIy6DuhB4vs6SWQhvPEQ3FZlECnIMiW3SDnbEXGnFQd0ReXfE3iFNhCUjLhAxEy1lBeKSLZd6JumwN3XvGlystGVLdMbea_UuOPPfgNyxKgociKSkWJOnB38yvg_Ig-Z5NtjtxS5HI2Mew_m2T5dX9owuTGZk8mlRa1SAucSG5Gz6jYJY8TtgURjRiMyaztAlavI6m1V4ghSaFa_KindlKWKcVIrvI0ya99hDNQqHLKMEjJElFJH4t4qVsVCXRFWp3MJja91qBPQE9LDmgG9Qc_DfABzKeqIuWOAYmAFbMlj1Ue5WoD6hdooh92B5496nEl8BRoGRyoV8OR5mnnW3I8kZRQNpWATUZx9hVPR8GFSTGgKTacpWrjZJlAF6hnEk8XdoThwaApRrw3ML9wy1jtSTMKBWCkrvhdNQ3LYKtmiZMNK9lS8fK4bnSz_X7MGBkJgdx42nee9sQ3IPGNQEUaoXJKdi5BG9ZFSH9Plz6gERmYnaY5-OslU6uXhkoOg6CFl_xFV5cRiPiClQ4Rb-uwztSW7KPp70v-oTYcKKpvAS-3L5jkC2y57cMVZf4vPH9Knpn2oT_s27ResQaBn7MFh2k_YEG_ncD3xm3k3h_Yx727bAOJ2V2D9jO0BA5rlqEhoVVYkrRNtmXSS45Mo1ESSZ7C0tyMkCAiioVG9AZoeNjVHqd97pH1QJElvOHpFnd3nYjZpDGADv2Gh-OrFWwh0l9edt1P-0edDu2yWvYsX60gChilp-UGtQ7YE55JNI0em0VQSVXW2tkPNBgiaQACjvbrgsYyk3uQZem7okh3ERjug6FjWkjb88H46AEYaguOqrNPM5naFTiU5v0Iz5Z5Dnp5CQf9JwqDXHuNFH1c5NNQ6BnwAGBlsntaGvsqpUpTNydD1ACstHdRozpexV14mF-VYr0GW7If47JBuGItIiBlRrx2wXhvr4Du4mOHfK2gkzbA6uCYiCtkSyL-bKJ5-qZ-2Ll0CCKsr0YDB9bq8__hsBg4KozJyfUMeG1A9Gwl1u5cx5gopY9WzRudkYjFtmUJYPAN-A0W_tCZiLUL5UTi9yCK5m6soMs09A5Yu2tmUEgAjs9P78IMfyZ3NyKKpso6mc268Ln5qzZrsn03-6fdgEHXIsuydcrhxzXnhf4x4qAQo4jsf3VQjA319t25wSVuBqQkW_P_DqoOas_uVyErlp6S_r4dpbM9cXcAUyGLy2-KNMdUZFibNGAhpaldRL6i1Cohv9n2sN_mFnNaOeFRC6qNsz_o7LXV3p-FyjFaecyxv7nKFO3SgbXhtfa1EM6TFa_zBPupXHkE3PRLsDa3cLZZA9oPOCDyLoHHA7NRyjlx07Mo-ZXIK6m3FIvEjUsMahTJlwEj5aKscBUz9F1AO0WuqhIj7bi7dOSaypwtMt9WaJRyVu6BnHl6T4p-dHa-dhY1DiOPVLiidLMaxF2lJwXQThdLnS8m_uvg389-d-C7SrRKX5_O3DUvWN5RdeE3QkX-rISTXb7_1JqzMw89UD1aZLQQ9Y5nlRtRoGZgB6s8awWS-Gv-KrdUDOiXaixoJcUyvqiUImX7gh4CG3wPk4HOK3fuXQ4V98jmeRKRVKGIQ4lPZxJpQekFsBXuHTVJB5g1BXtpiayVnfAALsscAPbBvMN41VNR4sKdMmbbi6rEiMyLch1h5qy9I5Jhx55MnsVgHYtqg1U6ka3diLoAy4NF6SwZyk2HdPOdDtgs6dKkVRFXIngePIh8KSSe330o0ILqEtMaZexhPRtJeLpzY6C-uoul4bOBuSh3AzC_V0INgNxVNFGH4r59e9czNTlN-nn7nYvadQFbAnXAKjec5GZBPxf4y0qZ-ONVM8m1SDwVFwOw4WK9cYtn35GxtVMNsSrxDoJfinV_qHpRz9Sk6SmIcVce9wE7er2AJo9oMVAGtLL0abLaj8n4tX6aTVZ5ueQxXUMI5D2ppqzrtPiwcxYda_QRoqODIS1BOWhDevFFD-glw2yBbnhjiI1Grm0SWsQ3s4nmjtDWrS21IwVrT3ctUukkW52ddDBgIGn4XTmjoSxwyC6ztNiwsEQBfYMr18zvhGhifN_mAn0FTC-WqU8mwKmLfUTCvt1QkOVxnvdBYrDExeTmeAW6UVd8rbJAKdYiwxwVceoQT_81JB63NzCz2o7XaeQRIenepbclfdRlNRNHdyNOsmyfzk51362r0GXGReZ7NqGbeHYQRKpwHLCO6agrcgIYdmrdgkl8c9UV2jTtgjtrUs4ZqEqL48dc9dEzUIRlkBYkmYFx-EUD1xVGXXoANtpgZOyzgNAf4mIXlu9Q3YbZl6lYXkLI3JpCP1KHRxeg3dXbivRXSCdoh8qO7viNOyM0LooL2Q3CaByCuFiHu_MyGZiBWK4TQDjwhBUJRCP0LoE92YU1DWISMRHhx0D5aQ0-jXzBbO2BidkrllZDd0JDMAMYWWFcFgKQm_w6NjR1YALOTleXHNVLbjYW0Wcw-MHo0AQ_7qg3UGQfx1abXF3yXeCemqcWORCyieWns09KpLK_7Z9_xmahds-fuxisd_PAiPFs0mt331op2jdW6iJKvetNAYKOl73gG8A0bYPlH7prbW1_IdBVAQG3DlCvRPGV-14nRV5XeVr5a_UtE9u1e3XJXdzwcr5AMOvWyeomPLleX0E0dyndMZiG4BlKrkfGzQ5DIBT501R29hNY2XTptYD7rMSAygvP8BVLeJxXKqKHrXT2i6yZG8IjAxnWSW3SRPrLk4s1GwucnDAUYYIMVhepLuQ6EaEhNUZdiMAYhzrHbExPNsItQzXgccwC_H1I6UYnT-6Vy61riL-O3Vyuj_aAIOvwW7rCU4QhtB4E9VrrvFkOji3Ex50jf56eG7fc4AOnPCKQz1Mr-aETFhaaoB1v9SlpqYHXx-9O4_fw4Tzyb2cvP75xuuFvTs9ev_no7Hr1YeFsPzl_e_7Lwi3JH94e_-P0l_jF8eI0fvPBOfz4_dm7449n5-_jk_P3r85euyda_P3s7dtF_OGY9m2d6G-T-XwOmjXb6TuNk2WNmWDYpNhJnqb6irvNg2RBvAqWRMdTEgLFBAaAU0oVUzMxv4F4wX6DIkaGysB817NFBwMsGi_llT1Pmq9j_ToL-Cq68qlY1MqRzyb4ioeMS86WG57sK7-YyTXWDFx0nKGO_mAqwGEiXUvReysY1bqXMS_l7BdBY2cezWsNIF6Ucl6V_PeKZ0sqyNPQ_vIA2X0_BkxmlTUlyTjlK1W32YcKmVaPZ-AhO-UGgJarVQTbv_BdmQVnMU_hHLruVmjYoczyr4Jf8_K4KJxVKyS5X3tpugZBNF1XqK4gMGNyjoz_qrQrYXquMZBlnqNbZ1Le84_9l2tQ5YH-v2zBKHU5f2-a-_frKfUlvhDlZfe6gWm9dZm4fcXCHSzpvD5u1Q66gfPkxkzg9ji7mwqWBzo7tUtVrNRl-BoTv4lkzZ2p3h66XJjXiestU0Waq1RczKEBVM38FX31mfamC8tuuJwfw4f1Lk12xWQXFqMskHFZP8Tqkq3XZp0TGvDx8ni9dsfGhudqvZOshm44MF3pkx1c9gE_5oV-ASwMRoGI_IQv4AXhfoO9vQFWy_GFy6GFsQQ4sDsISXBKuVgyBTTsAWtweo_z8_TB5-kkPzw0T-3XN50A7jcyW6A_EOj9-fwH-KHfSTrSqlMGpm29wUn9h4fPja_Ra-yYyl4f6dH6eOb9vMPDfz_v3Do17f0NNO_leQDaL-cZkPn8uasadDSpJN_vQ6PA2oZuHjkDXbihKT6Qm6eLBp1emqmuJunRrV48hnOdDZNxTtd-WVqvR-8p5G0yNheWUTCR7tIHal25gjCDSrYyBkUeD4zu3DC608hO0cIz0hCvuchLKO0lDMy1V1cX3ed0deDVSOdcdA_R1aMv7rl6-ptsU7_NQB1UWb36s6Gbhz1auEAIP_E6uEFQN6Xah0MoN1U8R_QPiMENM1faHIcPj9MXzNpKr3MrrCPmmpWaqzs9brcGE87axXON25ZEeYf1S9d3G0l-UanifGUdjGCaSkOb2l2Y_jwN2zRXcoivehfWevdhXCCOSyousM7lDBeAfdvBBWUma9MBz_eirui32L0P046Dg4DH5j8NQCigyryxMn0yehZ2gfnWdsHay7cO3sYicWT9vxi0B6SVoL7sJR1DkPdrO00eHxgJGV8LtfHM_1K_yT5udhrQCW-PJhC5yVjl7UM4OKa1VC3Oq7w0N3_aY20uIQXVjWdgVVZlEHLuSeewh32bb13ccIwhcaMArk3EXiGU2Na-gdvRWg4VraEaYe5YvKY01VNThv9ozV6Nq11FcPV3MuwugGZRjzvimIdkouVBJLpdxiJb5XvV002ThwTEhnSiTcuM1U3RqeZaiMzw3xGYadvL2aP2Cbmavm2W9iziA20jg2ShvgOuWMuB7TGww9up47wGpY11dEYxbT7shA6ecMYL74trvAP8AU5oT3ak44cOhTz-c3RxbNOR8mZEzOlsCgHAlolkejSlyPrzVG1AFj5Pj-AxYeUlpku_ARyrVL7YZcvpkSorPpuWebXe1D-02jT_W6duLFj2zzzf_1yXuIoZTKr1BPNK06Onjwl2evR1ejM9evRg_tOTh8-ePXv66Nnj-0-ePZhNd9Ojnx48nD999vD-w8cPnjx48PjJo2-z6Rea_P786ZNH9-Hvxx_vP3728PGTh9_-A9OgOOw)

- `src/`: Game engine, player, enemies, and skill classes
- `assets/`: Game assets (sprits, bgm, map, etc.)
- `data/`: Data storage for game statistics (CSV files)

## 🛠 Game Version
verion 1.0

## 👤 Creator

- Worakrit Kullanatpokin
- video [https://youtu.be/EJqSXPGo23g](https://youtu.be/rTT6APAU7Ag)

## 🤝 Credits
Sprite sheets: https://merchant-shade.itch.io/16x16-puny-characters<br/>
Map: https://merchant-shade.itch.io/16x16-puny-world<br/>
Background Music: https://www.FesliyanStudios.com
