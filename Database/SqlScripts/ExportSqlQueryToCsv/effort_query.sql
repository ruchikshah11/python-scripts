SET NOCOUNT ON;
SELECT *
FROM [bsone_1693759966].[dbo].[Project.Activity.Effort]
WHERE [AssignedToID] = 47
  AND [DBCreatedON] >= DATEADD(DAY, -30, GETUTCDATE())
  AND EntryTypeID = 2
ORDER BY ID DESC;
