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


- `src/`: Game engine, player, enemies, and skill classes
- `assets/`: Game assets (sprits, bgm, map, etc.)
- `data/`: Data storage for game statistics (CSV files)

## 🛠 Game Version
verion 1.0

## 👤 Creator
[![](https://mermaid.ink/img/pako:eNrNHGlv28j1rwj6UrorC4njdBNjEcBxnMRoLqySXbQIQIzFkTQ1RXI5Q9tKGv_2vvdmKB5zkN5su_UHiZp5c737GPrrdJknfHoyXaZMyheCrUu2_ZxNzB-1Tl6xLZ98bVrx74ciZTteTk4mH-ih18szvt3F6zKvCgB5hd9359h21wOUiikeb1nG1jQbrrXAtre6qQfOqkTkAHaK3_2pliXnGXQWuzXMMl9U5YoteQ9qmebLqwZICfg4w7YeXFllmcjWAHmZ52mv84Zd8zirtpe0Z5EpJ3LiDBF3MpGqfwxcOoajlyrGDQDMKs2Zcq0yCLWsypJnKtbQVyJN40oC6gA8EcswdMFuMp7ESC3BpfMoIhNKsFR84bE-VXTQxxSXXMV4JKurKHnBSu7upNVpI1bXcsOXV_EyT1MhRZ5Je80qsxdjlfQsBVustp4-la_XKRwOR7c7v_XFQDO6JQheIiecGO0Ft3hrCUNKBn1n9GCRPb0C0nCeeCguixLoFATZslvknK3ImJOqI_rikq9JnAJbSEomfCBCxhrKK0Uk-07UbXPgzmu-VHnZiOqWqc38F2o86sFvWJYADUVWVCpK1IG7m18D50f0OZtsc-SWIpeziWH_2STLb_pDEyY3NnsyqbSoRVrgRHI7ekbFrnicsC2IaMRgTGZtF7B6E0mtvUIMSQrV4kc9tZOyTClGcpWnSX7jI5yBQpVThkFKlohK-ljES92qSKAr0upkNrHptQZ9AnpackAzqD_4aYAPYD5VFSl3DEgErJgteazyKFcbUL9AE_2wO_DsUY8rgadAy-BAvRqONE8735LjiaSEsqkEbDKKs695OgouTIoBTbHhLFUbJ8sEukA9k3i6sCMMDwZNMeK9gfmZW8ZqT5pRKAAjdc3vq2lYBls1S5xtWMmWipendaOb7fdjxshICOTW077ztCe-AYlvBCrSCJVTsnMJ2rAuQvp7uvQBjcjA7DTNwZ8vmVq9NFRyGAQtvOQvurqMQMSXrHSIeFuHdaa2ZB9Nf1_yD7XhQFF9A3i5e84kX2DLXR-uKPN_4flT8sy0D_1h36b1ijUI_JwtOEz7AQv67QT-YdxGfvgd-_jhPttAYnbXoP0MLYHDmmVoSGgVliRtk22Z9JIj02iURJKnsDQ3IySIiGKhEb0BGh52tcdpn3tkPVBkCW94usXdXSdiNmkMoEO_4eH4agVbiPSXl1330_5ep0O7rJY9y1criAJG6Wm5Qa0D9oRnEk2jx2YRVFKVtXb2Aw2GSBqAgKP9uqCxzOQeZFn6rijSXQSG-2DomBbS9nwwPnoAhtqCo-rs00ymdgUOpXk_wrNlnoNeXsJB_4nCINdeI0UfF_k0FHoGPABYmeyelsa-SqnS1M3JEDUAK-1d1KiOV3EXHuZXpVivwZbsx7hsEK5YiwhImRGvXTDe2yug-_jYIV8r6KQNsDo4JuIa2ZKIP5tonr6tH3YuHYII66vRwIG1-vx_OCwGjgpjcnI9A14bED1bibU71zEmSumjVfNGZyRisW1ZAhh8DX6DhT90JmLtQjmR-D2IorkbK-gyDb0D1u6aGRQSgNP35_dhhj-SuxsRRVNlncxmXfjc_FmbNdm-2_3TbsCga5Fl2Trl8OOG80L_GHFQiFFE9r86KMaGevvu3OASNwNSkq35fwdVB7Vn94uQFUvPSX_fjdLZnrg7gKmQxeW3RZpjKjKsTRqwkNLULiJfUWqVkN9se9hvc4s5rZzwqAXVxtnvdPbaau-PQuUYrTzm2N9cZYp26cDa8Fr7WgjnyYrXeYL9VK48Am76BVibOzjbrAHtBxwQeZfA44HZKOWcuOlZlPxa5JXUW4pF4sYlBjWK5MuAkXJRVriKGfouoJ0iV1WJkXbcXTpyTWXOFplvKzRKOSv3QM48vSdFPzo7XzuLGoeRRypcUbpZDeKu0pMCaKeLpc4XE_918O9nv3vwXSVapa9PF-6aFyzvqLrwW6Eif1bCyS7ff2rN2ZmHHqgeLTJaiHrLs8qNKFAzsINVnrUCSfw1f5lbKgb0SzUWtJJiGV9WSpGyfU4PgQ2-g8lA55U79y6Hintk8zyJSKpQxKHEpzOJtKD0AtgK946apAPMmoK9tETWyk54AJdlDgD7YN5hvOqpKHHhThmz7WVVYkTmRbmOMHPW3hHJsGNPJs9isI5FtcEqncjWbkRdguXBonSWDOWmQ7r5XgdslnRp0qqIKxE8Dx5EvhASz-8-FGhBdYVpjTL2sJ6NJDzde2OgvrqLpeGzgbkodwMwv1VCDYDcVzRRh-K-fXvXMzU5Tfp5952L2nUBWwJ1wCo3nORmQT8X-MtKmfjjVTPJjUg8FRcDsOFivXGLZ9-RsbVTDbEq8Q6CX4p1f6h6Uc_UpOkpiHFXHvcBO3q9gCaPaDFQBrSy9Gmy2o_J-I1-mk1WebnkMV1DCOQ9qaas67T4sHMWHWv0EaKjgyEtQTloQ3rxRQ_oJcNsgW54Y4iNRq5tElrEN7OJ5o7Q1q0ttSMFa0_3LVLpJFudnXQwYCBp-F05o6EscMgus7TYsLBEAX2DK9fM74RoYnzf5gJ9BUwvlqlPJsCpi31Ewr7dUJDlcZ73QWKwxMXk5nQFulFXfK2yQCnWIsMcFXHqEE__OSQetzcws9qO12nkESHp3qW3JX3UZTUTR3cjTrJsny7Odd-dq9BlxkXmezahm3h2EESqcBywjumoK3ICGHZq3YJJfHPVFdo07YI7a1LOGahKi-PHXPXRM1CEZZAWJJmBcfhFA9cVRl16ADbaYGTss4DQH-JiF5bvUd2G2ZepWF5ByNyaQj9Sh0cXoN3V24r0V0gnaIfKju74rTsjNC6KC9kNwmgcgrhch7vzMhmYgViuE0A48IQVCUQj9C6BPdmlNQ1iEjER4cdA-WkNPo18zmztgYnZa5ZWQ3dCQzADGFlhXBYCkJv8JjY0dWACzk5XlxzVS242FtFnMPjB6NAEP-6oN1BkH8dWm1xd8V3gnpqnFjkQsonlp4tPSqSyv-2ffsJmoXbPnrkYrHfzwIjxbNJrd99aKdo3VuoiSr3rTQGCjpe94BvANG2D5R-6a21tfyHQVQEBtw5Qr0TxlfteJ0Ve13la-Wv1LRPbtXt1yV3c8nK-QDDr1snqNjy5Xl9BNHcl3TGYhuAZSq5Hxs0OQyAU-dNUdvYTWNl06bWA-6zEgMoLz_AVS3icVyqih6109ousmRvCIwMZ1klt0kT6y5OLNRsLnJwwFGGCDFYXqS7kOhGhITVGXYjAGIc6x2xMTzbCLUM14HHMAvx9SOlGJ0_ulcuda4i_jt1cro_2gCDr8Fu6wlOEIbQeBPVa67xZDo4txMedI3-evjduucEHTnlCIJ-nVvJDJywsNEE73upT0lIDr07fnsfv4MN55F8vXnx87XTDX59fvHr90dn18sPC2X72_s37nxduSf7w5vQf5z_Hz08X5_HrD87hp-8u3p5-vHj_Lj57_-7lxSv3RIu_X7x5s4g_nNK-rRP9ZTKfz0GzZjt9p3GyrDETDJsUO8vTVF9xt3mQLIhXwZLoeEpCoJjAAHBKqWJqJua3EC_Yb1DEyFAZmO96tuhggEXjpby250nzdaxfZwFfRVc-FYtaOfLZBF_xkHHJ2XLDk33lFzO5xpqBi44z1NEfTAU4TKRrKXpvBaNa9zLmpZz9ImjszKN5rQHEi1LOq5L_VvFsSQV5GtpfHiC778eAyayypiQZp3yl6jb7UCHT6vEMPGSn3ADQcrWKYPuXviuz4CzmKZxD190KDTuUWf5F8BtenhaFs2qFJPdrL03XIIim6wrVFQRmTM6R8V-WdiVMzzUGssxzdOtMynv-sf9yDao80P9XLRilrubvTHP_fj2lvsQXorzsXjcwrXcuE7evWLiDJZ3Xx63aQTdwntyYCdweZ3dTwfJAZ6d2qYqVugxfY-JXkay5M9XbQ5cL8zpxvWWqSHOViss5NICqmb-krz7T3nZh2S2X81P4sN6lya6Z7MJilAUyLuuHWF2x9dqsc0YDPl6drtfu2NjwXK13ktXQDQemK32yg8s-4Me80C-AhcEoEJGf8AW8INyvsLfXwGo5vnA5tDCWAAd2ByEJTikXS6aAhj1gDU7vcX6ePvw8neSHh-ap_fqmE8D9RmYL9K8E-mA-_yv80O8knWjVKQPTtt7gpP7Dw2fG1-g1dkxlr4_0aH08837e4eG_n3VunZr2_gaa9_I8AO2X8wzIfP7MVQ06mVSS7_ehUWBtQzePnIEu3NAUH8jN00WDTi_NVFeT9OhWLx7Duc6GyTina78srdej9xTyNhmbC8somEh36QO1rlxBmEElWxmDIo8HRnduGN1rZKdo4RlpiNdc5CWU9hIG5tqrq4vuc7o68Gqkcy66h-jq0Rf3XD39Tbap32agDqqsXv3Z0M3DHi1cIISfeB3cIKibUu3DIZSbKp4j-gfE4IaZK22Ow4fH6QtmbaXXuRXWEXPNSs3VnR63W4MJZ-3iucZtS6K8w_ql6_uNJL-oVHG-sg5GME2loU3tLkx_noZtmis5xFe9C2u9-zAuEMclFRdY53KGC8C-7eCCMpO16YDne15X9Fvs3odpx8FBwFPznwYgFFBl3liZPhk9C7vAfGu7YO3lWwdvY5E4sv5fDNoD0kpQX_aSjiHI-7WdJo8PjISMb4TaeOZ_od9kHzc7DeiEtycTiNxkrPL2IRwc01qqFudVXpqbP-2xNpeQgurGM7AqqzIIOfekc9jDvs23Lm44xpC4UQDXJmKvEEpsa9_A7Wgth4rWUI0wdyxeU5rqqSnDf7Rmr8bVriK4-jsZdhdAs6jHHXHMQzLR8iAS3S5jka3yverppslDAmJDOtGmZcbqpuhUcy1EZvjvCMy07eXsUfuEXE3fNkt7FvGBtpFBslDfAVes5cD2GNjh7dRxXoPSxjo6o5g2H3ZCB08444X3xTXeAf4AJ7QnO9LxQ4dCHv85uji26Uh5MyLmdDaFAGDLRDI9mVJk_XmqNiALn6cn8Jiw8grTpd8AjlUqX-yy5fRElRWfTcu8Wm_qH1ptmv-tUzcWLPtnnu9_rktcxQwm1XqGeaXpyeMjgp2efJ3eTk8OHz758Wj--OGT46dHT54-eXR0DN276cnxo_mj46OjJw-ePD0-evDo6eNvs-kXmv54fnT8t-OHPz4-Ojp-9OD46Nt_AMqDOM4?type=png)](https://mermaid.live/edit#pako:eNrNHGlv28j1rwj6UrorC4njdBNjEcBxnMRoLqySXbQIQIzFkTQ1RXI5Q9tKGv_2vvdmKB5zkN5su_UHiZp5c737GPrrdJknfHoyXaZMyheCrUu2_ZxNzB-1Tl6xLZ98bVrx74ciZTteTk4mH-ih18szvt3F6zKvCgB5hd9359h21wOUiikeb1nG1jQbrrXAtre6qQfOqkTkAHaK3_2pliXnGXQWuzXMMl9U5YoteQ9qmebLqwZICfg4w7YeXFllmcjWAHmZ52mv84Zd8zirtpe0Z5EpJ3LiDBF3MpGqfwxcOoajlyrGDQDMKs2Zcq0yCLWsypJnKtbQVyJN40oC6gA8EcswdMFuMp7ESC3BpfMoIhNKsFR84bE-VXTQxxSXXMV4JKurKHnBSu7upNVpI1bXcsOXV_EyT1MhRZ5Je80qsxdjlfQsBVustp4-la_XKRwOR7c7v_XFQDO6JQheIiecGO0Ft3hrCUNKBn1n9GCRPb0C0nCeeCguixLoFATZslvknK3ImJOqI_rikq9JnAJbSEomfCBCxhrKK0Uk-07UbXPgzmu-VHnZiOqWqc38F2o86sFvWJYADUVWVCpK1IG7m18D50f0OZtsc-SWIpeziWH_2STLb_pDEyY3NnsyqbSoRVrgRHI7ekbFrnicsC2IaMRgTGZtF7B6E0mtvUIMSQrV4kc9tZOyTClGcpWnSX7jI5yBQpVThkFKlohK-ljES92qSKAr0upkNrHptQZ9AnpackAzqD_4aYAPYD5VFSl3DEgErJgteazyKFcbUL9AE_2wO_DsUY8rgadAy-BAvRqONE8735LjiaSEsqkEbDKKs695OgouTIoBTbHhLFUbJ8sEukA9k3i6sCMMDwZNMeK9gfmZW8ZqT5pRKAAjdc3vq2lYBls1S5xtWMmWipendaOb7fdjxshICOTW077ztCe-AYlvBCrSCJVTsnMJ2rAuQvp7uvQBjcjA7DTNwZ8vmVq9NFRyGAQtvOQvurqMQMSXrHSIeFuHdaa2ZB9Nf1_yD7XhQFF9A3i5e84kX2DLXR-uKPN_4flT8sy0D_1h36b1ijUI_JwtOEz7AQv67QT-YdxGfvgd-_jhPttAYnbXoP0MLYHDmmVoSGgVliRtk22Z9JIj02iURJKnsDQ3IySIiGKhEb0BGh52tcdpn3tkPVBkCW94usXdXSdiNmkMoEO_4eH4agVbiPSXl1330_5ep0O7rJY9y1criAJG6Wm5Qa0D9oRnEk2jx2YRVFKVtXb2Aw2GSBqAgKP9uqCxzOQeZFn6rijSXQSG-2DomBbS9nwwPnoAhtqCo-rs00ymdgUOpXk_wrNlnoNeXsJB_4nCINdeI0UfF_k0FHoGPABYmeyelsa-SqnS1M3JEDUAK-1d1KiOV3EXHuZXpVivwZbsx7hsEK5YiwhImRGvXTDe2yug-_jYIV8r6KQNsDo4JuIa2ZKIP5tonr6tH3YuHYII66vRwIG1-vx_OCwGjgpjcnI9A14bED1bibU71zEmSumjVfNGZyRisW1ZAhh8DX6DhT90JmLtQjmR-D2IorkbK-gyDb0D1u6aGRQSgNP35_dhhj-SuxsRRVNlncxmXfjc_FmbNdm-2_3TbsCga5Fl2Trl8OOG80L_GHFQiFFE9r86KMaGevvu3OASNwNSkq35fwdVB7Vn94uQFUvPSX_fjdLZnrg7gKmQxeW3RZpjKjKsTRqwkNLULiJfUWqVkN9se9hvc4s5rZzwqAXVxtnvdPbaau-PQuUYrTzm2N9cZYp26cDa8Fr7WgjnyYrXeYL9VK48Am76BVibOzjbrAHtBxwQeZfA44HZKOWcuOlZlPxa5JXUW4pF4sYlBjWK5MuAkXJRVriKGfouoJ0iV1WJkXbcXTpyTWXOFplvKzRKOSv3QM48vSdFPzo7XzuLGoeRRypcUbpZDeKu0pMCaKeLpc4XE_918O9nv3vwXSVapa9PF-6aFyzvqLrwW6Eif1bCyS7ff2rN2ZmHHqgeLTJaiHrLs8qNKFAzsINVnrUCSfw1f5lbKgb0SzUWtJJiGV9WSpGyfU4PgQ2-g8lA55U79y6Hintk8zyJSKpQxKHEpzOJtKD0AtgK946apAPMmoK9tETWyk54AJdlDgD7YN5hvOqpKHHhThmz7WVVYkTmRbmOMHPW3hHJsGNPJs9isI5FtcEqncjWbkRdguXBonSWDOWmQ7r5XgdslnRp0qqIKxE8Dx5EvhASz-8-FGhBdYVpjTL2sJ6NJDzde2OgvrqLpeGzgbkodwMwv1VCDYDcVzRRh-K-fXvXMzU5Tfp5952L2nUBWwJ1wCo3nORmQT8X-MtKmfjjVTPJjUg8FRcDsOFivXGLZ9-RsbVTDbEq8Q6CX4p1f6h6Uc_UpOkpiHFXHvcBO3q9gCaPaDFQBrSy9Gmy2o_J-I1-mk1WebnkMV1DCOQ9qaas67T4sHMWHWv0EaKjgyEtQTloQ3rxRQ_oJcNsgW54Y4iNRq5tElrEN7OJ5o7Q1q0ttSMFa0_3LVLpJFudnXQwYCBp-F05o6EscMgus7TYsLBEAX2DK9fM74RoYnzf5gJ9BUwvlqlPJsCpi31Ewr7dUJDlcZ73QWKwxMXk5nQFulFXfK2yQCnWIsMcFXHqEE__OSQetzcws9qO12nkESHp3qW3JX3UZTUTR3cjTrJsny7Odd-dq9BlxkXmezahm3h2EESqcBywjumoK3ICGHZq3YJJfHPVFdo07YI7a1LOGahKi-PHXPXRM1CEZZAWJJmBcfhFA9cVRl16ADbaYGTss4DQH-JiF5bvUd2G2ZepWF5ByNyaQj9Sh0cXoN3V24r0V0gnaIfKju74rTsjNC6KC9kNwmgcgrhch7vzMhmYgViuE0A48IQVCUQj9C6BPdmlNQ1iEjER4cdA-WkNPo18zmztgYnZa5ZWQ3dCQzADGFlhXBYCkJv8JjY0dWACzk5XlxzVS242FtFnMPjB6NAEP-6oN1BkH8dWm1xd8V3gnpqnFjkQsonlp4tPSqSyv-2ffsJmoXbPnrkYrHfzwIjxbNJrd99aKdo3VuoiSr3rTQGCjpe94BvANG2D5R-6a21tfyHQVQEBtw5Qr0TxlfteJ0Ve13la-Wv1LRPbtXt1yV3c8nK-QDDr1snqNjy5Xl9BNHcl3TGYhuAZSq5Hxs0OQyAU-dNUdvYTWNl06bWA-6zEgMoLz_AVS3icVyqih6109ousmRvCIwMZ1klt0kT6y5OLNRsLnJwwFGGCDFYXqS7kOhGhITVGXYjAGIc6x2xMTzbCLUM14HHMAvx9SOlGJ0_ulcuda4i_jt1cro_2gCDr8Fu6wlOEIbQeBPVa67xZDo4txMedI3-evjduucEHTnlCIJ-nVvJDJywsNEE73upT0lIDr07fnsfv4MN55F8vXnx87XTDX59fvHr90dn18sPC2X72_s37nxduSf7w5vQf5z_Hz08X5_HrD87hp-8u3p5-vHj_Lj57_-7lxSv3RIu_X7x5s4g_nNK-rRP9ZTKfz0GzZjt9p3GyrDETDJsUO8vTVF9xt3mQLIhXwZLoeEpCoJjAAHBKqWJqJua3EC_Yb1DEyFAZmO96tuhggEXjpby250nzdaxfZwFfRVc-FYtaOfLZBF_xkHHJ2XLDk33lFzO5xpqBi44z1NEfTAU4TKRrKXpvBaNa9zLmpZz9ImjszKN5rQHEi1LOq5L_VvFsSQV5GtpfHiC778eAyayypiQZp3yl6jb7UCHT6vEMPGSn3ADQcrWKYPuXviuz4CzmKZxD190KDTuUWf5F8BtenhaFs2qFJPdrL03XIIim6wrVFQRmTM6R8V-WdiVMzzUGssxzdOtMynv-sf9yDao80P9XLRilrubvTHP_fj2lvsQXorzsXjcwrXcuE7evWLiDJZ3Xx63aQTdwntyYCdweZ3dTwfJAZ6d2qYqVugxfY-JXkay5M9XbQ5cL8zpxvWWqSHOViss5NICqmb-krz7T3nZh2S2X81P4sN6lya6Z7MJilAUyLuuHWF2x9dqsc0YDPl6drtfu2NjwXK13ktXQDQemK32yg8s-4Me80C-AhcEoEJGf8AW8INyvsLfXwGo5vnA5tDCWAAd2ByEJTikXS6aAhj1gDU7vcX6ePvw8neSHh-ap_fqmE8D9RmYL9K8E-mA-_yv80O8knWjVKQPTtt7gpP7Dw2fG1-g1dkxlr4_0aH08837e4eG_n3VunZr2_gaa9_I8AO2X8wzIfP7MVQ06mVSS7_ehUWBtQzePnIEu3NAUH8jN00WDTi_NVFeT9OhWLx7Duc6GyTina78srdej9xTyNhmbC8somEh36QO1rlxBmEElWxmDIo8HRnduGN1rZKdo4RlpiNdc5CWU9hIG5tqrq4vuc7o68Gqkcy66h-jq0Rf3XD39Tbap32agDqqsXv3Z0M3DHi1cIISfeB3cIKibUu3DIZSbKp4j-gfE4IaZK22Ow4fH6QtmbaXXuRXWEXPNSs3VnR63W4MJZ-3iucZtS6K8w_ql6_uNJL-oVHG-sg5GME2loU3tLkx_noZtmis5xFe9C2u9-zAuEMclFRdY53KGC8C-7eCCMpO16YDne15X9Fvs3odpx8FBwFPznwYgFFBl3liZPhk9C7vAfGu7YO3lWwdvY5E4sv5fDNoD0kpQX_aSjiHI-7WdJo8PjISMb4TaeOZ_od9kHzc7DeiEtycTiNxkrPL2IRwc01qqFudVXpqbP-2xNpeQgurGM7AqqzIIOfekc9jDvs23Lm44xpC4UQDXJmKvEEpsa9_A7Wgth4rWUI0wdyxeU5rqqSnDf7Rmr8bVriK4-jsZdhdAs6jHHXHMQzLR8iAS3S5jka3yverppslDAmJDOtGmZcbqpuhUcy1EZvjvCMy07eXsUfuEXE3fNkt7FvGBtpFBslDfAVes5cD2GNjh7dRxXoPSxjo6o5g2H3ZCB08444X3xTXeAf4AJ7QnO9LxQ4dCHv85uji26Uh5MyLmdDaFAGDLRDI9mVJk_XmqNiALn6cn8Jiw8grTpd8AjlUqX-yy5fRElRWfTcu8Wm_qH1ptmv-tUzcWLPtnnu9_rktcxQwm1XqGeaXpyeMjgp2efJ3eTk8OHz758Wj--OGT46dHT54-eXR0DN276cnxo_mj46OjJw-ePD0-evDo6eNvs-kXmv54fnT8t-OHPz4-Ojp-9OD46Nt_AMqDOM4)

- Worakrit Kullanatpokin
- video [https://youtu.be/EJqSXPGo23g](https://youtu.be/rTT6APAU7Ag)

## 🤝 Credits
Sprite sheets: https://merchant-shade.itch.io/16x16-puny-characters<br/>
Map: https://merchant-shade.itch.io/16x16-puny-world<br/>
Background Music: https://www.FesliyanStudios.com
