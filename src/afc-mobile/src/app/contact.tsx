import { Linking, StyleSheet, TouchableOpacity, Text, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing } from '@/constants/theme';
import IconRow from '@/components/icon-text-row';
import IconRowRightChevron from '@/components/icon-text-right-chevron';
import IconColumn from '@/components/icon-text-column';
import { useColorScheme } from 'react-native';
import {Colors} from '@/constants/theme';




import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

import Feather from '@expo/vector-icons/Feather';
import Entypo from '@expo/vector-icons/Entypo';
import { colorScheme } from 'nativewind';


export default function ContactScreen() {
 
  return (
    <View className="flex-1 gap-3 items-center bg-card dark:bg-card-dark">

      <Card className='w-11/12 mt-5'>
      <View className="flex border-b border-gray-500 pb-5 gap-5">
        <CardHeader>
          <CardTitle className='text-sm'>QUICK CONTACT</CardTitle>
        </CardHeader>
        <CardContent className='flex gap-3'>
            <IconRowRightChevron icon={<Feather name="phone" size={18} color="gray" />} text="123-456-7890" />
            <IconRowRightChevron icon={<Feather name="mail" size={18} color="gray" />} text="info@afcsacramento.org" />
            <IconRowRightChevron icon={<Feather name="map-pin" size={18} color="gray" />} text="7842 Elmont Ave, Elverta, CA 95626" />
        </CardContent>
      </View>
      <View className="flex gap-3">
        <CardHeader>
          <CardTitle className='text-sm'>SERVICE TIMES</CardTitle>
        </CardHeader>
        <CardContent className='flex gap-5'>
          <IconRow icon={<Feather name="clock" size={18} color="gray" />} text="Sunday Services: 11:00 AM & 5:00 PM" />
          <IconRow icon={<Feather name="clock" size={18} color="gray" />} text="Wednesday Bible Study: 7:00 PM" />
        </CardContent>
      </View>
      </Card>
      
      <Card className='w-11/12 bg-blue-100 dark:bg-card-dark'>
        <CardHeader>
          <CardTitle className='text-sm'>SEND A MESSAGE</CardTitle>
        </CardHeader>
        <CardContent>
          <Text>Card Content</Text>
        </CardContent>
      </Card>

      <Card className='w-11/12'>
        <CardHeader>
          <CardTitle className='text-sm'>CONNECT WITH US</CardTitle>
        </CardHeader>
        <CardContent className='px-5'>
          <View className='flex-row gap-5'>
            <Card className="flex-1">
              <IconColumn icon={<Entypo name="instagram" size={24} color="#E1306C" />} text="Instagram" />
            </Card>
            <Card className="flex-1">
              <IconColumn icon={<Entypo name="youtube" size={24} color="red" />} text="YouTube" />
            </Card>
            <Card className="flex-1">
              <IconColumn icon={<Entypo name="facebook" size={24} color="blue" />} text="Facebook" />
            </Card>
          </View>
        </CardContent>
      </Card>
    </View>
  );
}

