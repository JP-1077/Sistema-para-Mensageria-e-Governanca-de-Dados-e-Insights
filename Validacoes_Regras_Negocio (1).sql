#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # VALIDAÇÃO: VOLUMES PARCIAIS E ABSOLUTOS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
/*
Objetivo: 
  Encontrar maneira de retornar dados de solicitações, cancelamentos e IR de maneira parcial.

Descrição:
  Precisamos comparar os volumes de hora em hora mas de maneira percentual. Desta forma, a volumetria de solicitações, cancelamento e IR necessita ser de 
  acordo com o horario e não de acordo com o dia
*/

SELECT
  DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) AS DATA_D_3,
  CURRENT_TIME("America/Sao_Paulo") AS HORARIO_ATUAL_REFERENCIA,
  COUNT(DATA_OFERTA) AS TOTAL_SOLICITACOES_D_3_PARCIAL
FROM `tim-sdbx-resjourney-3175.dm_prod.TB_CRC_ULTRATAB` 
WHERE
  DATA_OFERTA >= TIMESTAMP_SUB(TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), DAY), INTERVAL 3 DAY)
  AND DATA_OFERTA < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 DAY);


SELECT
  DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AS DATA_D_7,
  CURRENT_TIME("America/Sao_Paulo") AS HORARIO_ATUAL_REFERENCIA,
  COUNT(DATA_OFERTA) AS TOTAL_SOLICITACOES_D_7_PARCIAL
FROM `tim-sdbx-resjourney-3175.dm_prod.TB_CRC_ULTRATAB` 
WHERE
  DATA_OFERTA >= TIMESTAMP_SUB(TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), DAY), INTERVAL 7 DAY)
  AND DATA_OFERTA < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY);



#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # VALIDAÇÃO: VARIAÇÃO DOS DADOS DE ACORDO COM O DIA
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

/*
Objetivo: 
  Encontrar maneira de retornar dados de D-1 quando o dia vigente está presente em (terça, quarta, quinta e sexta). Porém, quando for segunda ele retorna 
  dados de D-3

Descrição:
  O objetivo é encontrar uma maneira de retornar dados de diferentes dias de acordo com o dia vigente
*/

CREATE TEMP FUNCTION filtragem_dados ()
RETURNS DATE AS (
  CASE 
    WHEN EXTRACT(DAYOFWEEK FROM CURRENT_DATE()) = 2 THEN DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
    ELSE DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  END
);

SELECT * FROM `tim-sdbx-resjourney-3175.dm_prod.TB_CRC_ULTRATAB`  WHERE DATE(DATA_OFERTA) = filtragem_dados() LIMIT 5;



#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                          # VALIDAÇÃO: VARIAÇÃO DOS DADOS DE ACORDO COM O DIA
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/

/*
Objetivo: 
  Encontrar variação entre os diferentes periodos que for retornado na consulta.

Descrição:
  O objetivo é termos uma noção melhor das variaçoes entre os dias
*/

SELECT 
  'TB_CRC_ULTRATAB' AS Nome_Tabela,
  MAX(DATA_OFERTA) AS DATA_MAXIMA,
  SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) AS VOLUME_LINHAS_D_1,
  SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) AS VOLUME_LINHAS_D_3,
  SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS VOLUME_LINHAS_D_7,
  SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) - SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) AS DELTA_D1_D3,
  SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) - SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS DELTA_D1_D7,
  (
    SAFE_DIVIDE(
      (
        SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) -
        SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) 
      ),
      SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END)
    )*100
  ) AS VAR_D1_D_3_PERC,

  (
    SAFE_DIVIDE(
      (
        SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) -
        SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) 
      ),
      SUM(CASE WHEN DATE(DATA_OFERTA) = DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END)
    )*100
  ) AS VAR_D1_D_7_PERC,

FROM `tim-sdbx-resjourney-3175.dm_prod.TB_CRC_ULTRATAB`;