from webcrawler import WEBCRAWLER

payload = {'cpf': '08795786619'}
PAGE_CMSP = WEBCRAWLER().get_cabinet_table(payload)