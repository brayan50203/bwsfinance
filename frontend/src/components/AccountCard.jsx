import React from 'react';

const colorMap = {
  purple: 'from-purple-600 to-indigo-600',
  blue: 'from-blue-500 to-blue-400',
  green: 'from-green-500 to-green-400',
  red: 'from-red-500 to-orange-500',
  orange: 'from-yellow-500 to-orange-400'
};

export default function AccountCard({ title, value, color = 'blue', icon }) {
  const gradient = colorMap[color] || colorMap.blue;
  return (
    <div className={`rounded-xl p-5 text-white shadow-lg bg-gradient-to-r ${gradient} hover:scale-105 transition-transform`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm opacity-90">{title}</p>
          <p className="text-2xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-3xl opacity-30">{icon ? '💠' : ''}</div>
      </div>
    </div>
  );
}
