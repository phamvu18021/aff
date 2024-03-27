// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import type { NextApiRequest, NextApiResponse } from "next";
import { json } from "stream/consumers";

type Data = {
  status: string;
  data: any;
};

import Cors from "micro-cors";

// Initialize CORS
const cors = Cors({
  allowMethods: ["POST"], // Specify the allowed HTTP methods
});

const handler = async (req: NextApiRequest, res: NextApiResponse<Data>) => {
  const header = req.headers;
  const method = req.method;
  const requestBody = req.body;
  console.log("requestBody:", requestBody);
  if (method === "POST" && requestBody != null) {
    const data = await th_set_cookie(
      requestBody.link_tracker,
      requestBody.odoo_utmParams,
      requestBody.code,
      requestBody.referrer
    );
    const dataCookie = await call_server();
    dataCookie.results.code = data;
    console.log(dataCookie);
    res.status(200).json({ status: "success!", data: dataCookie });
  }

  res.status(200).json({ status: "200", data: "success" });
};

async function th_set_cookie(
  fullUrl: string,
  utmParams: any,
  code: any,
  referrer: any
) {
  if (Object.keys(utmParams).length) {
    return await count_click(fullUrl, utmParams, code, referrer);
  }
}

async function call_server() {
  const url_fetch = "https://odoo.cors.ongdev.online/api/check_cookie";
  let response = await fetch(url_fetch);
  let data = response != undefined ? await response.json() : {};
  return data;
}

async function count_click(
  fullUrl: any,
  utmParams: any,
  code: any,
  referrer: any
) {
  console.log("code :" + code);
  const url_server = "https://odoo.cors.ongdev.online/api/backlink";
  let data = {
    link_tracker: fullUrl.split("?")[0],
    odoo_utmParams: utmParams,
    code: code,
    referrer: referrer,
  };
  let headers = new Headers({
    "Content-Type": "application/json",
    Authorization: "7fd3b7621caf03334a5036e6550adbc7b8311ecc",
  });

  let result = await fetch(url_server, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((result) => {
      return result["result"]["code"];
    })
    .catch((error) => {
      console.error("Error:", error);
      return false;
    });
  console.log("result :" + result);
  return result;
}

export default cors(handler as any);
