SET NOCOUNT ON;

SELECT
    [TenantID],
    [SubscriptionIdentifier],
    [ClientState],
    [SiteUrl],
    [NotificationUrl],
    [Resource],
    [ExpiresOn],
    [ChangeToken],
    [IsDeleted],
    [ChangeType],
    [ContactID],
    [DBModifiedOn],
    [UpdateSource]
FROM [dbo].[Common.Tenant.Subscription] WITH (NOLOCK);
