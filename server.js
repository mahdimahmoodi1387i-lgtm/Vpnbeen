const express=require("express");
const app=express();
app.use(express.json());
app.use(express.static(__dirname));
app.post("/api/send",async(req,res)=>{
 const {dateType,date,time}=req.body||{};
 const token=process.env.TELEGRAM_BOT_TOKEN,chatId=process.env.TELEGRAM_CHAT_ID;
 if(!token||!chatId)return res.status(500).json({ok:false});
 const text=`💍 قرار جدید پرنسس!\n\nدیت: ${dateType}\nتاریخ: ${date}\nساعت: ${time}`;
 try{
  const r=await fetch(`https://api.telegram.org/bot${token}/sendMessage`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({chat_id:chatId,text})});
  res.status(r.ok?200:502).json(await r.json());
 }catch(e){res.status(502).json({ok:false})}
});
app.listen(process.env.PORT||3000);