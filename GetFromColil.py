from copy import copy
from time import sleep
import SendRequest
from bs4 import BeautifulSoup
import pandas as pd


paras = {"query": """prefix colil: <http://purl.jp/bio/10/colil/ontology/201303#>
        prefix bibo: <http://purl.org/ontology/bibo/>
        prefix dc: <http://purl.org/dc/elements/1.1/>
        prefix doco: <http://purl.org/spar/doco/>
        prefix togows: <http://togows.dbcls.jp/ontology/ncbi-pubmed#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?ctpmid ?title ?authors ?source ?year ?section ?ctpmcid ?comment (count(?ctctpmid) as ?citedBy) where {
        {select * where {
            ?context colil:mentions ?pmid_uri;
                rdf:value ?comment.
            ?secnode doco:contains ?context;
                dc:title ?section.
            ?citing doco:contains ?secnode;
                rdfs:seeAlso ?ctpmuri.
            ?ctpmuri rdf:type colil:PubMed;
                colil:Authors ?authors;
                togows:dp ?year;
                togows:so ?source;
                togows:ti ?title;
                togows:pmid ?ctpmid.
            VALUES ?pmid_uri { <http://purl.jp/bio/10/colil/id/%s> }
        } order by DESC(?year) offset %s limit 40}
        optional {?citing colil:pmcid ?ctpmcid.}
        optional {
            ?ctciting doco:contains / doco:contains / colil:mentions ?citing;
            rdfs:seeAlso [
                rdf:type colil:PubMed;
                togows:pmid ?ctctpmid ].
        }
        }
        """
}

def getOnePage(pmid, offset):
    cur_paras = paras.copy()
    cur_paras["query"] = cur_paras["query"]%(pmid, offset)
    req = SendRequest.SendRequest("http://colil.dbcls.jp/Colil?", cur_paras)
    xmlDoc = req.byGet()
    soup = BeautifulSoup(xmlDoc, "xml")
    pageSummary = list()

    for singleResult in soup.find_all("result"):
        record = {}
        for field in singleResult.contents:
            if(str(field) == "\n"):
                continue
            record[field["name"]] = field.string        
        pageSummary.append(record)

    return pageSummary

def getAllPages(pmid):
    originalOffset = 0
    summary = []
    while(True):
        pageSummary = getOnePage(pmid, originalOffset)
        if(len(pageSummary) == 0):
            break
        else:
            summary = summary + pageSummary
            originalOffset += 40
            sleep(0.5)
  
    return summary
     
if __name__ == "__main__":
    ORIGINAL_PMID = "31296739"
    summary = getAllPages(ORIGINAL_PMID)
    df = pd.DataFrame(summary)
    writer = pd.ExcelWriter(ORIGINAL_PMID + ".xlsx")
    df.to_excel(writer, "sheet1")
    writer.save()