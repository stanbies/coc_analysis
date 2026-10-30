'use client';

import { useSyncExternalStore } from 'react';
import { Clan } from '../types';
import GameIcon from './GameIcon';
import ResourceBar from './ResourceBar';

const noopSubscribe = () => () => {};

// Shown on the parchment instead of the in-game clan description.
// Set to '' to show the description from the game again.
const WELCOME_TEXT = 'Welkom kleine zwegers op de officiële Zwegerneet analyse website';

interface ClanHeaderProps {
  clan: Clan;
  lastUpdated: string;
}

export default function ClanHeader({ clan, lastUpdated }: ClanHeaderProps) {
  const totalWars = clan.warWins + clan.warTies + clan.warLosses;
  const winRate = totalWars > 0 ? (clan.warWins / totalWars) * 100 : 0;

  // Formatted in the browser so it shows the visitor's local time; the page is
  // pre-rendered on the server, which would otherwise print UTC.
  const updatedText = useSyncExternalStore(
    noopSubscribe,
    () => new Date(lastUpdated).toLocaleString(),
    () => '',
  );

  return (
    <header className="coc-wood p-5 md:p-6 mb-6">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div className="flex items-center gap-4 min-w-0">
          {clan.badgeUrls?.large && (
            <img
              src={clan.badgeUrls.large}
              alt={clan.name}
              className="w-20 h-20 md:w-24 md:h-24 shrink-0 drop-shadow-[0_4px_0_rgba(0,0,0,0.45)]"
            />
          )}
          <div className="min-w-0">
            <h1 className="coc-text text-3xl md:text-4xl leading-tight break-words">{clan.name}</h1>
            <p className="coc-text text-sm opacity-90">{clan.tag}</p>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              <span className="coc-chip coc-text text-sm pl-1.5 pr-3 py-0.5 whitespace-nowrap flex items-center gap-1.5">
                <GameIcon name="star" size={20} /> Level {clan.clanLevel}
              </span>
              {clan.location && (
                <span className="coc-chip coc-text text-sm px-3 py-0.5 whitespace-nowrap">
                  {clan.location.name}
                </span>
              )}
              {clan.warLeague && (
                <span className="coc-chip coc-text text-sm pl-1.5 pr-3 py-0.5 whitespace-nowrap flex items-center gap-1.5">
                  <GameIcon name="cwl" size={20} /> {clan.warLeague.name}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-3 w-full lg:w-[440px] shrink-0">
          <ResourceBar icon="barbarian" label="Members" value={`${clan.members}/50`}
                       color="#7fd0ff" fill={(clan.members / 50) * 100} />
          <ResourceBar icon="trophy" label="Clan Points" value={clan.clanPoints.toLocaleString('en-US')}
                       color="#ffd84a" />
          <ResourceBar icon="clanWar" label="War Wins" value={clan.warWins.toLocaleString('en-US')}
                       color="#e05bd6" />
          <ResourceBar icon="threeStars" label="Win Rate" value={`${winRate.toFixed(1)}%`}
                       color="#a3e256" fill={winRate} />
        </div>
      </div>

      {(WELCOME_TEXT || clan.description) && (
        <p className="coc-parchment mt-5 px-4 py-3 text-sm leading-relaxed">
          {WELCOME_TEXT || clan.description}
        </p>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mt-4">
        <div className="flex flex-wrap items-center gap-2">
          {clan.labels?.map((label, i) => (
            <span key={i} className="coc-chip flex items-center gap-1.5 pl-1 pr-3 py-0.5 whitespace-nowrap">
              {label.iconUrls?.small && (
                <img src={label.iconUrls.small} alt="" className="w-6 h-6" />
              )}
              <span className="coc-text text-xs">{label.name}</span>
            </span>
          ))}
        </div>
        <p className="coc-text text-xs opacity-90">
          Last updated: {updatedText}
        </p>
      </div>
    </header>
  );
}
