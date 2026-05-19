import * as React from 'react';
import { Circle, Path, Svg } from 'react-native-svg';

type UserIconProps = {
  color?: string;
  size?: number;
};

export function User({ color = 'currentColor', size = 24 }: UserIconProps) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Circle cx="12" cy="7" r="4" stroke={color} strokeWidth="2" />
      <Path d="M5.5 21c0-4.5 3-7 7.5-7s7.5 2.5 7.5 7" stroke={color} strokeWidth="2" strokeLinecap="round" />
    </Svg>
  );
}
