import { PropsWithChildren } from "react";
import { StyleSheet, Text, View } from "react-native";
export function SectionCard({title,children}:PropsWithChildren<{title:string}>){return <View style={styles.card}><Text style={styles.title}>{title}</Text>{children}</View>}
const styles=StyleSheet.create({card:{flexGrow:1,flexBasis:320,minHeight:120,padding:18,borderRadius:16,backgroundColor:"#FFFFFF",borderWidth:1,borderColor:"#E2E8E0",gap:10},title:{fontSize:15,fontWeight:"700",color:"#263229"}});