import { View, Text } from "react-native";

interface IconRowProps {
  icon: React.ReactNode;
  text: string;
}

export default function IconRow({ icon, text }: IconRowProps) {
  return (
    <View className="flex-row items-center gap-3 ">
      {icon}
      <Text className="text-base">{text}</Text>
    </View>
  );
}