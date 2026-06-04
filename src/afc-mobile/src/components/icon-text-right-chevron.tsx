import Entypo from "@expo/vector-icons/build/Entypo";
import { View, Text } from "react-native";

interface IconRowProps {
  icon: React.ReactNode;
  text: string;
}

export default function IconRowRightChevron({ icon, text }: IconRowProps) {
  return (
    <View className="flex-row items-center gap-3 ">
      {icon}
      <Text className="text-base">{text}</Text>
      <Entypo name="chevron-small-right" size={24} color="gray" />
    </View>
  );
}