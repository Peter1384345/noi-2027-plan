# -*- coding: utf-8 -*-
# 生成带 BOM 的 PowerShell 查询脚本(避免 PowerShell 5.1 按 ANSI 误读中文)
content = r'''[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$out = @()
try {
    $conn = New-Object -ComObject ADODB.Connection
    $conn.Open('Provider=Search.CollatorDSO;Extended Properties=''Application=Windows''')
    foreach ($q in @('regedit', '注册表', '注册表编辑器', 'control', '控制面板', 'winver', '记事本')) {
        $out += ('=== QUERY: ' + $q + ' ===')
        $sql = ('SELECT TOP 10 "System.ItemNameDisplay", "System.ItemPathDisplay" FROM SYSTEMINDEX WHERE "System.ItemNameDisplay" LIKE ''%' + $q + '%''')
        try {
            $rs = $conn.Execute($sql)
            $n = 0
            while (-not $rs.EOF) {
                $out += ('  ' + $rs.Fields.Item('System.ItemNameDisplay').Value + '  |  ' + $rs.Fields.Item('System.ItemPathDisplay').Value)
                $rs.MoveNext()
                $n++
            }
            if ($n -eq 0) { $out += '  (NO RESULT)' }
            $rs.Close()
        } catch {
            $out += ('  ERROR: ' + $_.Exception.Message)
        }
    }
    $conn.Close()
} catch {
    $out += ('FATAL: ' + $_.Exception.Message)
}
$out | Out-File -FilePath 'C:\Users\Administrator\WorkBuddy\2026-09-14-22-25-54\wb_search_test.txt' -Encoding UTF8
'''
with open(r'C:\Users\Administrator\WorkBuddy\2026-09-14-22-25-54\wb_search_test.ps1', 'w', encoding='utf-8-sig') as f:
    f.write(content)
print('written with BOM')
