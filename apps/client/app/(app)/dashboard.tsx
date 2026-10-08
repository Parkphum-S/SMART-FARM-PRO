import { StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { RoleBadge } from "@/components/RoleBadge";
import { SectionCard } from "@/components/SectionCard";
import { currentUser } from "@/config/session";

export default function DashboardScreen() {
  return <SafeAreaView style={styles.safe}><View style={styles.container}>
    <Text style={styles.eyebrow}>SMART FARM PRO</Text>
    <View style={styles.header}><View><Text style={styles.title}>Farm Dashboard</Text><Text style={styles.subtitle}>Web + iOS + Android shared shell</Text></View><RoleBadge role={currentUser.role}/></View>
    <SectionCard title="System status"><Text style={styles.body}>Frontend shell is ready. Backend, MQTT, device control, and live telemetry remain outside this checkpoint.</Text></SectionCard>
    <View style={styles.grid}><SectionCard title="Farms"><Text style={styles.metric}>—</Text><Text style={styles.caption}>No live data connected</Text></SectionCard><SectionCard title="Alerts"><Text style={styles.metric}>—</Text><Text style={styles.caption}>No alert source connected</Text></SectionCard></View>
  </View></SafeAreaView>;
}
const styles=StyleSheet.create({
  safe:{flex:1,backgroundColor:"#F6F8F5"},
  container:{width:"100%",maxWidth:1180,alignSelf:"center",padding:24,gap:18},
  eyebrow:{fontSize:12,fontWeight:"700",letterSpacing:1.5,color:"#5B6B5D"},
  header:{flexDirection:"row",alignItems:"center",justifyContent:"space-between",gap:16},
  title:{fontSize:32,fontWeight:"800",color:"#172119"},
  subtitle:{marginTop:4,fontSize:15,color:"#68766B"},
  body:{fontSize:15,lineHeight:23,color:"#4F5D52"},
  grid:{flexDirection:"row",flexWrap:"wrap",gap:16},
  metric:{fontSize:30,fontWeight:"800",color:"#172119"},
  caption:{marginTop:4,fontSize:13,color:"#78847A"}
});
