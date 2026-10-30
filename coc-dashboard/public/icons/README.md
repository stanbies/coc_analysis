# Game icons

Official Clash of Clans art from Supercell's fan kit
(https://fankit.supercell.com/d/vkEdmkUCngKw/game-assets), used under
Supercell's Fan Content Policy (https://supercell.com/en/fan-content-policy/).
The footer of every page carries the required unofficial notice.

Each file is the fan kit PNG with its transparent padding trimmed, centred on
a square and scaled down to at most 128px. Nothing else is changed: the
policy doesn't allow modifying Supercell assets.

`trophy.svg` is the exception: our own drawing of a home-village trophy,
because the fan kit has no regular trophy icon. Replace it if one turns up.

| File | Fan kit asset |
|---|---|
| barbarian.png | Icon_HV_Barbarian |
| barbarian-king.png | Icon_HV_Hero_Barbarian_King |
| battle.png | Icon_BB_Battle |
| capital-gold.png | Icon_CC_Resource_Capital_Gold_big |
| capital-hall.png | Building_CC_Capital_Hall_level_10 |
| capital-trophy.png | Icon_CC_Resource_Capital_Trophy |
| clan-war.png | Icon_HV_Clan_War |
| crown.png | hero pet upgrade crown |
| cwl.png | Icon_HV_CWL_Crystal_1 |
| district-hall.png | Building_CC_District_Hall_ level_5 |
| legend-shield.png | legend_shield |
| magnifier.png | magnifying_glass |
| raid.png | Icon_CC_Raid_1 |
| spells.png | Icon_HV_donate_Spells |
| standard-shield.png | standard_shield |
| star.png | Icon_BB_Star |
| three-stars.png | Icon_BB_3_Stars |
| town-hall.png | Building_HV_Town_Hall_level_16_1 |
| troops.png | Icon_HV_donate_Troops |
| upgrade-hammer.png | building upgrade hammer |

To add one: search the fan kit (the page supports `?q=<name>`), download the
PNG, trim and scale it the same way, and add it to `ICONS` in
`app/components/GameIcon.tsx`.
