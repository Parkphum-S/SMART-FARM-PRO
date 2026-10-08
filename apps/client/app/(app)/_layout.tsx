import { Tabs } from "expo-router";
import { Platform } from "react-native";
export default function AppLayout() {
  return <Tabs screenOptions={{headerShown:false,tabBarStyle:{height:Platform.OS==="web"?64:72,paddingTop:6,paddingBottom:8}}}>
    <Tabs.Screen name="dashboard" options={{title:"Dashboard"}}/>
    <Tabs.Screen name="farms" options={{title:"Farms"}}/>
    <Tabs.Screen name="alerts" options={{title:"Alerts"}}/>
    <Tabs.Screen name="settings" options={{title:"Settings"}}/>
  </Tabs>;
}
