AZRAEL_GET_LENDINGS_QUERY = """
{
    lendings(orderBy: cursor, orderDirection: desc, first: $first, skip: $skip) {
        id
        cursor,
        lenderAddress
        maxRentDuration
        dailyRentPrice
        lentAmount
        nftPrice
        paymentToken
        nftAddress
        tokenId
        lentAt
    }
}
"""

AZRAEL_GET_RENTINGS_QUERY = """
{
    rentings(orderBy: cursor, orderDirection: desc, first: $first, skip: $skip) {
        id,
        cursor,
        renterAddress,
        rentDuration,
        rentedAt,
        lending {
            id,
            lenderAddress,
            paymentToken,
            nftPrice,
            dailyRentPrice,
            lenderAddress,
            nftAddress,
            tokenId
        }
    }
}
"""


SYLVESTER_GET_LENDINGS_QUERY = """
{
    lendings(orderBy: cursor, orderDirection: desc, first: $first, skip: $skip) {
        id,
        cursor,
        lenderAddress,
        maxRentDuration,
        dailyRentPrice,
        lendAmount,
        paymentToken,
        nftAddress,
        tokenID,
        lentAt
    }
}
"""


SYLVESTER_GET_RENTINGS_QUERY = """
{
    rentings(orderBy: cursor, orderDirection: desc, where: {expired: false}, first: $first, skip: $skip) {
        id,
        cursor,
        renterAddress,
        rentDuration,
        rentedAt,
        lending {
            id,
            lenderAddress,
            paymentToken,
            dailyRentPrice,
            lenderAddress,
            nftAddress,
            tokenID
        }
    }
}
"""

WHOOPI_GET_LENDINGS_QUERY = """
{
    lendings(orderBy: cursor, orderDirection: desc, first: $first, skip: $skip) {
        id,
        cursor,
        lenderAddress,
        maxRentDuration,
        paymentToken,
        nftAddress,
        tokenId,
        lentAt,
        upfrontRentFee,
        revShareBeneficiaries,
        revSharePortions
    }
}
"""


WHOOPI_GET_RENTINGS_QUERY = """
{
    rentings(orderBy: cursor, orderDirection: desc, where: {expired: false}, first: $first, skip: $skip) {
        id,
        cursor,
        renterAddress,
        rentDuration,
        rentedAt,
        lending {
            id,
            lenderAddress,
            paymentToken,
            lenderAddress,
            nftAddress,
            tokenId,
            upfrontRentFee,
            revShareBeneficiaries,
            revSharePortions
        }
    }
}
"""
