import { View, Text } from "react-native";

interface IconRowProps {
  icon: React.ReactNode;
  text: string;
}

export default function IconColumn({ icon, text }: IconRowProps) {
  return (
    <View className="flex-col items-center">
      {icon}
      <Text className="text-sm">{text}</Text>
    </View>
  );
}