const alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
export function freshCodes(count) {
  if(!Number.isInteger(count)||count<1||count>100)throw Error('一次可生成 1 至 100 个访问码。');
  const codes=new Set();
  while(codes.size<count){const chars=[...crypto.getRandomValues(new Uint8Array(8))].map(v=>alphabet[v&31]).join('');codes.add('HW-'+chars.slice(0,4)+'-'+chars.slice(4));}
  return [...codes];
}
export function csv(rows){return '\ufeff'+rows.map(row=>row.map(value=>{let text=String(value??'');if(/^[\s]*[=+\-@]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';}).join(',')).join('\r\n');}
export function statusOf(code,today){if(code.is_active!==1)return ['已停用','off'];if(code.expiry&&code.expiry<today)return ['已过期','muted'];if((code.essays_used||0)>=code.essays_total||(code.new_essays_total>0&&(code.new_essays_used||0)>=code.new_essays_total))return ['额度已用完','muted'];return ['可使用',''];}
export function remaining(code){const total=Math.max(0,code.essays_total-(code.essays_used||0));return {total,fresh:code.new_essays_total>0?Math.min(total,Math.max(0,code.new_essays_total-(code.new_essays_used||0))):total};}
