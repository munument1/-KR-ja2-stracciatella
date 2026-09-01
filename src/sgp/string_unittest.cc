#include "gtest/gtest.h"

#include <string_theory/string>


TEST(stringTest, English)
{
	const ST::string str = "test";
	EXPECT_EQ(str.size(), 4u);
	EXPECT_EQ(str[0], '\x74');
	EXPECT_EQ(str[1], '\x65');
	EXPECT_EQ(str[2], '\x73');
	EXPECT_EQ(str[3], '\x74');
	EXPECT_EQ(str[4], '\0');
}

TEST(stringTest, RussianWithUnicodeConsts)
{
	const ST::string str = u8"\u0442\u0435\u0441\u0442";
	EXPECT_EQ(str.size(), 8u);
	EXPECT_EQ(str[0], '\xD1');
	EXPECT_EQ(str[1], '\x82');
	EXPECT_EQ(str[2], '\xD0');
	EXPECT_EQ(str[3], '\xB5');
	EXPECT_EQ(str[4], '\xD1');
	EXPECT_EQ(str[5], '\x81');
	EXPECT_EQ(str[6], '\xD1');
	EXPECT_EQ(str[7], '\x82');
	EXPECT_EQ(str[8], '\0');
}

TEST(stringTest, Russian)
{
	const ST::string str = "тест";
	EXPECT_EQ(str.size(), 8u);
	EXPECT_EQ(str[0], '\xD1');
	EXPECT_EQ(str[1], '\x82');
	EXPECT_EQ(str[2], '\xD0');
	EXPECT_EQ(str[3], '\xB5');
	EXPECT_EQ(str[4], '\xD1');
	EXPECT_EQ(str[5], '\x81');
	EXPECT_EQ(str[6], '\xD1');
	EXPECT_EQ(str[7], '\x82');
	EXPECT_EQ(str[8], '\0');
}

TEST(stringTest, Chinese)
{
	const ST::string str = "测试";
	ASSERT_EQ(str.size(), 6u);
	EXPECT_EQ(str[0], '\xE6');
	EXPECT_EQ(str[1], '\xB5');
	EXPECT_EQ(str[2], '\x8B');
	EXPECT_EQ(str[3], '\xE8');
	EXPECT_EQ(str[4], '\xAF');
	EXPECT_EQ(str[5], '\x95');
	EXPECT_EQ(str[6], '\0');
}

TEST(stringTest, Greek)
{
	const ST::string str = "δοκιμή";
	ASSERT_EQ(str.size(), 12u);
	EXPECT_EQ(str[0], '\xCE');
	EXPECT_EQ(str[1], '\xB4');
	EXPECT_EQ(str[2], '\xCE');
	EXPECT_EQ(str[3], '\xBF');
	EXPECT_EQ(str[4], '\xCE');
	EXPECT_EQ(str[5], '\xBA');
	EXPECT_EQ(str[6], '\xCE');
	EXPECT_EQ(str[7], '\xB9');
	EXPECT_EQ(str[8], '\xCE');
	EXPECT_EQ(str[9], '\xBC');
	EXPECT_EQ(str[10], '\xCE');
	EXPECT_EQ(str[11], '\xAE');
	EXPECT_EQ(str[12], '\0');
}

TEST(stringTest, Korean)
{
	const ST::string str = "한국어 테스트";
	ASSERT_EQ(str.size(), 19u);
	auto u32 = str.to_utf32();
	ASSERT_EQ(u32.size(), 7u);
	EXPECT_EQ(u32[0], char32_t(0xD55C)); // 한
	EXPECT_EQ(u32[1], char32_t(0xAD6D)); // 국
	EXPECT_EQ(u32[2], char32_t(0xC5B4)); // 어
	EXPECT_EQ(u32[3], char32_t(0x0020)); // ' '
	EXPECT_EQ(u32[4], char32_t(0xD14C)); // 테
	EXPECT_EQ(u32[5], char32_t(0xC2A4)); // 스
	EXPECT_EQ(u32[6], char32_t(0xD2B8)); // 트
}

TEST(stringTest, KoreanMercEdtQuote0)
{
	const ST::string str = "하하 적군이 왔군!";
	auto u32 = str.to_utf32();
	ASSERT_EQ(u32.size(), 10u);
	EXPECT_EQ(u32[0], char32_t(0xD558)); // 하
	EXPECT_EQ(u32[1], char32_t(0xD558)); // 하
	EXPECT_EQ(u32[2], char32_t(0x0020)); // ' '
	EXPECT_EQ(u32[3], char32_t(0xC801)); // 적
	EXPECT_EQ(u32[4], char32_t(0xAD60)); // 군
	EXPECT_EQ(u32[5], char32_t(0xC774)); // 이
	EXPECT_EQ(u32[6], char32_t(0x0020)); // ' '
	EXPECT_EQ(u32[7], char32_t(0xC654)); // 왔
	EXPECT_EQ(u32[8], char32_t(0xAD70)); // 군
	EXPECT_EQ(u32[9], char32_t(0x0021)); // !
}

